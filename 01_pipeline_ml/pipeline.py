# pipeline.py

import argparse
import logging
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score, classification_report
import joblib
from datetime import datetime
from google.cloud import storage

# Configurar logging
logging.basicConfig(level=logging.INFO)

def run_pipeline(args):
    """
    Función principal que ejecuta el pipeline de entrenamiento.
    """
    # =================================================================
    # 1. INGESTA DE DATOS DESDE GCS
    # =================================================================
    logging.info(f"Iniciando la ingesta de datos desde {args.gcs_data_path}...")
    data = pd.read_csv(args.gcs_data_path)
    logging.info("Datos cargados exitosamente.")
    logging.info(f"Shape de los datos: {data.shape}")

    # =================================================================
    # 2. LIMPIEZA DE DATOS
    # =================================================================
    logging.info("Iniciando limpieza de datos...")
    data.drop_duplicates(inplace=True)
    # En un escenario real, se debe definir una estrategia de imputación robusta.
    # Por ahora, se eliminan filas con nulos si las hubiera.
    data.dropna(inplace=True)
    logging.info("Limpieza de datos completada.")

    # =================================================================
    # 3. FEATURE ENGINEERING
    # =================================================================
    logging.info("Iniciando feature engineering...")
    analysis_date = datetime.strptime('2025-08-07', '%Y-%m-%d')
    data['signup_date'] = pd.to_datetime(data['signup_date'])
    data['last_purchase_date'] = pd.to_datetime(data['last_purchase_date'])
    data['days_since_last_purchase'] = (analysis_date - data['last_purchase_date']).dt.days
    data['customer_lifetime_days'] = (analysis_date - data['signup_date']).dt.days
    data['purchases_per_lifetime'] = data['total_purchases'] / (data['customer_lifetime_days'] + 1)
    logging.info("Feature engineering completado.")

    # =================================================================
    # 4. PREPROCESAMIENTO Y ENTRENAMIENTO
    # =================================================================
    logging.info("Iniciando preprocesamiento y entrenamiento del modelo...")
    X = data.drop(['customer_id', 'signup_date', 'last_purchase_date', 'churned'], axis=1)
    y = data['churned']

    categorical_features = ['gender']
    numerical_features = X.select_dtypes(include=np.number).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ], remainder='passthrough')

    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42))
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    param_grid = {
        'classifier__n_estimators': [100, 200, 300],
        'classifier__max_depth': [3, 5, 7],
        'classifier__learning_rate': [0.05, 0.1],
        'classifier__subsample': [0.8, 1.0]
    }

    grid_search = GridSearchCV(
        model_pipeline,
        param_grid,
        cv=3,
        scoring='roc_auc',
        verbose=1,
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)

    logging.info(f"Mejores parámetros encontrados: {grid_search.best_params_}")
    logging.info(f"Mejor puntaje ROC AUC (CV): {grid_search.best_score_:.4f}")

    best_model = grid_search.best_estimator_

    # Evaluación en Test
    y_pred_proba = best_model.predict_proba(X_test)[:, 1]
    test_roc_auc = roc_auc_score(y_test, y_pred_proba)
    logging.info(f"ROC AUC en el conjunto de prueba: {test_roc_auc:.4f}")

    # =================================================================
    # 5. GUARDAR MODELO EN GCS
    # =================================================================
    logging.info(f"Guardando el modelo en {args.gcs_model_output_dir}...")
    model_filename = 'model.pkl'
    local_model_path = f"/tmp/{model_filename}"
    joblib.dump(best_model, local_model_path)
    
    # Extraer bucket y path del argumento GCS
    bucket_name = args.gcs_model_output_dir.replace("gs://", "").split("/")[0]
    blob_path = "/".join(args.gcs_model_output_dir.replace("gs://", "").split("/")[1:] + [model_filename])
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    
    blob.upload_from_filename(local_model_path)
    logging.info(f"Modelo guardado exitosamente en {args.gcs_model_output_dir}/{model_filename}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--gcs-data-path',
        type=str,
        required=True,
        help='Ruta GCS al archivo clientes.csv'
    )
    parser.add_argument(
        '--gcs-model-output-dir',
        type=str,
        required=True,
        help='Directorio GCS donde se guardará el modelo entrenado.'
    )
    
    arguments = parser.parse_args()
    run_pipeline(arguments)