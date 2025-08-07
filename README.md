# MLE GCP Challenge

## Descripción General

Este proyecto implementa una solución completa de MLOps en Google Cloud Platform (GCP) para un modelo de predicción de churn (abandono de clientes). La solución abarca todo el ciclo de vida del modelo, desde la preparación de datos hasta el monitoreo en producción, siguiendo las mejores prácticas de MLOps.

## Estructura del Proyecto

```
.
├── 00_data/                   # Datos de entrenamiento y prueba
├── 01_pipeline_ml/            # Pipeline de ML para entrenamiento y evaluación
├── 02_terraform_infra/        # Infraestructura como código con Terraform
├── 03_versioning_retraining/  # Versionado de modelos y reentrenamiento
├── 04_monitoring_eval/        # Monitoreo y evaluación de modelos
├── 05_bonus_investigacion/    # Investigación sobre LLMOps
└── README.md                 
```

## Componentes Principales

### 1. Pipeline de ML (01_pipeline_ml)

Implementación del pipeline de machine learning para la predicción de churn, que incluye:

- Preprocesamiento de datos
- Feature engineering
- Entrenamiento de modelos (XGBoost, RandomForest, LogisticRegression)
- Evaluación y selección del mejor modelo
- Exportación del modelo para su despliegue

### 2. Infraestructura como Código (02_terraform_infra)

Configuración de la infraestructura en GCP utilizando Terraform:

- Buckets de Cloud Storage
- Datasets de BigQuery
- Instancias de Vertex AI
- Configuración de IAM y permisos

### 3. Versionado y Reentrenamiento (03_versioning_retraining)

Sistema de versionado de modelos y flujo de reentrenamiento utilizando MLFlow:

- Experimentación con diferentes modelos
- Registro del modelo campeón en MLFlow Model Registry
- Promoción automática de modelos entre etapas (staging, production)
- Comparación de métricas para decidir cuándo actualizar el modelo en producción

### 4. Monitoreo y Evaluación (04_monitoring_eval)

Sistema de monitoreo para detectar derivas y problemas en el modelo desplegado:

- Detección de data drift y concept drift
- Monitoreo de métricas de rendimiento del modelo (ROC AUC, Precision, Recall)
- Monitoreo de métricas operacionales (latencia, tasa de errores)
- Configuración de alertas y dashboards
- Estrategias de test A/B y rollback

### 5. Investigación sobre LLMOps (05_bonus_investigacion)

Investigación sobre la adaptación de la ML Factory para trabajar con modelos de lenguaje grandes (LLMs):

- Diferencias entre MLOps tradicional y LLMOps
- Adaptación de cada etapa del pipeline para LLMs
- Consideraciones especiales para fine-tuning, evaluación y monitoreo de LLMs

## Requisitos

- Python 3.11+
- Google Cloud SDK
- Terraform
- MLFlow
- Pandas, Scikit-learn, XGBoost

## Configuración

1. Configura tu cuenta de GCP y establece las credenciales:

```bash
gcloud auth application-default login
```

2. Despliega la infraestructura con Terraform:

```bash
cd 02_terraform_infra
terraform init
terraform apply
```

3. Ejecuta el pipeline de ML:

```bash
cd 01_pipeline_ml
python train_pipeline.py
```

4. Configura el versionado y reentrenamiento con MLFlow:

```bash
cd 03_versioning_retraining
mlflow ui
# En otra terminal
mlflow run . -e experiment
```

## Monitoreo

Para configurar el monitoreo del modelo en producción, sigue las instrucciones en el README de la carpeta `04_monitoring_eval`.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir los cambios propuestos antes de enviar un pull request.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
