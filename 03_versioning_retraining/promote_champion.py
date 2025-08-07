import argparse
import logging
from mlflow.tracking import MlflowClient

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s [%(levelname)s] %(message)s")

def main(model_name):
    client = MlflowClient()
    try:
        staging_versions = client.get_latest_versions(name=model_name, stages=["Staging"])
        if not staging_versions:
            logging.info(f"No hay modelos en 'Staging' para '{model_name}'. Saliendo.")
            return
        
        candidate_version = staging_versions[0]
        logging.info(f"Modelo candidato encontrado: Versión {candidate_version.version} en Staging.")
        run_candidate = client.get_run(candidate_version.run_id)
        # Usamos la métrica del conjunto de test, que es más fiable que la de CV
        metric_candidate = run_candidate.data.metrics["test_roc_auc"]
        logging.info(f"Métrica del candidato (Test ROC AUC): {metric_candidate:.4f}")

        prod_versions = client.get_latest_versions(name=model_name, stages=["Production"])
        if not prod_versions:
            logging.info("No hay modelo en 'Production'. Promoviendo el candidato directamente.")
            client.transition_model_version_stage(name=model_name, version=candidate_version.version, stage="Production", archive_existing_versions=True)
            return

        prod_version = prod_versions[0]
        logging.info(f"Modelo de producción encontrado: Versión {prod_version.version}.")
        run_prod = client.get_run(prod_version.run_id)
        metric_prod = run_prod.data.metrics["test_roc_auc"]
        logging.info(f"Métrica de producción (Test ROC AUC): {metric_prod:.4f}")
        
        if metric_candidate > metric_prod:
            logging.info("¡El candidato es mejor! Promoviendo a 'Production'.")
            client.transition_model_version_stage(name=model_name, version=prod_version.version, stage="Archived")
            client.transition_model_version_stage(name=model_name, version=candidate_version.version, stage="Production")
        else:
            logging.info("El candidato no supera al modelo en producción. No se realizarán cambios.")
    except Exception as e:
        logging.error(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str, required=True)
    args = parser.parse_args()
    main(args.model_name)