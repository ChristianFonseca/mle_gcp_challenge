# src/mlflow_pipeline.py

import argparse
import logging
import pandas as pd
from datetime import datetime

import mlflow
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s [%(levelname)s] %(message)s")

def run_pipeline(args):
    """
    Función principal que ejecuta el pipeline de entrenamiento, experimentación y registro en MLFlow.
    """
    # =================================================================
    # Iniciar un run de MLFlow para encapsular todo el proceso
    # =================================================================
    mlflow.set_experiment(args.experiment_name)
    with mlflow.start_run() as run:
        logging.info(f"Iniciando run de MLFlow: {run.info.run_id}")
        
        # =================================================================
        # INGESTA, LIMPIEZA Y FEATURE ENGINEERING (Lógica de tu pipeline.py)
        # =================================================================
        logging.info(f"Iniciando la ingesta de datos desde {args.gcs_data_path}...")
        data = pd.read_csv(args.gcs_data_path)
        logging.info("Datos cargados exitosamente.")

        logging.info("Iniciando limpieza de datos...")
        data.drop_duplicates(inplace=True)
        data.dropna(inplace=True)

        logging.info("Iniciando feature engineering...")
        analysis_date = datetime.strptime('2025-08-07', '%Y-%m-%d')
        data['signup_date'] = pd.to_datetime(data['signup_date'])
        data['last_purchase_date'] = pd.to_datetime(data['last_purchase_date'])
        data['days_since_last_purchase'] = (analysis_date - data['last_purchase_date']).dt.days
        data['customer_lifetime_days'] = (analysis_date - data['signup_date']).dt.days
        data['purchases_per_lifetime'] = data['total_purchases'] / (data['customer_lifetime_days'] + 1)
        logging.info("Lógica del pipeline original completada.")

        # =================================================================
        # PREPROCESAMIENTO Y EXPERIMENTACIÓN
        # =================================================================
        X = data.drop(['customer_id', 'signup_date', 'last_purchase_date', 'churned'], axis=1)
        y = data['churned']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

        preprocessor = ColumnTransformer(transformers=[
            ('num', StandardScaler(), X.select_dtypes(include=pd.np.number).columns.tolist()),
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['gender'])
        ])

        # Ejemplos de algoritmos a competir
        models_to_train = {
            "LogisticRegression": (LogisticRegression(solver='liblinear'), {'classifier__C': [0.1, 1.0]}),
            "RandomForest": (RandomForestClassifier(), {'classifier__n_estimators': [100, 200]}),
            "XGBoost": (XGBClassifier(use_label_encoder=False, eval_metric='logloss'), {'classifier__learning_rate': [0.05, 0.1]})
        }
        
        best_score = -1
        champion_model = None
        champion_model_name = "churn-champion-model"

        logging.info("Iniciando experimentación con múltiples modelos...")
        for model_name, (model, param_grid) in models_to_train.items():
            logging.info(f"--- Entrenando y tuneando: {model_name} ---")
            pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', model)])
            grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='roc_auc', n_jobs=-1)
            grid_search.fit(X_train, y_train)
            if grid_search.best_score_ > best_score:
                best_score = grid_search.best_score_
                champion_model = grid_search.best_estimator_
                champion_model_name = model_name

        logging.info(f"Modelo campeón: {champion_model_name} con ROC AUC (CV) de {best_score:.4f}")
        
        # =================================================================
        # REGISTRO DEL MODELO CAMPEÓN EN MLFLOW
        # =================================================================
        
        # Evaluar el campeón en el conjunto de test
        final_roc_auc = roc_auc_score(y_test, champion_model.predict_proba(X_test)[:, 1])
        
        # Loggear todo en el run principal de MLFlow
        mlflow.log_param("champion_model_type", champion_model_name)
        mlflow.log_metric("best_cv_roc_auc", best_score)
        mlflow.log_metric("final_test_roc_auc", final_roc_auc)
        mlflow.set_tag("status", "champion_selected")

        logging.info(f"Registrando el modelo campeón '{champion_model_name}' en el Model Registry...")
        
        # MLFlow gestiona el guardado del artefacto y el registro del modelo.
        mlflow.sklearn.log_model(
            sk_model=champion_model,
            artifact_path="model", # Nombre de la carpeta dentro del artefacto del run
            registered_model_name=args.registered_model_name
        )
        
        logging.info("Pipeline de MLFlow completado exitosamente.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Argumentos del pipeline original
    parser.add_argument('--gcs-data-path', type=str, required=True)
    # Argumentos nuevos para MLFlow
    parser.add_argument('--experiment-name', type=str, default="Churn_Experiment_Pipeline")
    parser.add_argument('--registered-model-name', type=str, default="churn-final-model")
    
    args = parser.parse_args()
    run_pipeline(args)