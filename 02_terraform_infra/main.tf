# main.tf

# Configura el proveedor de Google Cloud
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.50.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Habilitación de las APIs necesarias para el proyecto de MLOps
resource "google_project_service" "gcp_apis" {
  # El for_each permite habilitar múltiples APIs de forma concisa.
  for_each = toset([
    "aiplatform.googleapis.com",
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "iam.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com"
  ])

  project                    = var.project_id
  service                    = each.key
  disable_dependent_services = true
}

# Creación de la cuenta de servicio para Vertex AI Pipelines
# Esta cuenta ejecutará los trabajos con permisos restringidos.
resource "google_service_account" "vertex_sa" {
  project      = var.project_id
  account_id   = var.service_account_id
  display_name = "Service Account for Vertex AI Pipelines"
  depends_on   = [google_project_service.gcp_apis]
}

# Asignación de los roles IAM mínimos necesarios a la cuenta de servicio
# En un entorno de producción estricto, se podrían asignar roles
# a nivel de recurso (ej. solo a un bucket específico) en lugar de a nivel de proyecto.
resource "google_project_iam_member" "iam_bindings" {
  for_each = toset([
    "roles/aiplatform.user",         # Para crear y ejecutar trabajos en Vertex AI
    "roles/storage.objectAdmin",     # Para leer/escribir artefactos y datos en GCS
    "roles/bigquery.dataEditor",     # Para leer/escribir en tablas de BigQuery
    "roles/iam.serviceAccountUser"   # Para permitir que otros servicios usen esta cuenta
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.vertex_sa.email}"
}

# Creación del bucket de Google Cloud Storage
# Este bucket almacenará datos, modelos y otros artefactos del pipeline.
resource "google_storage_bucket" "ml_bucket" {
  project                     = var.project_id
  name                        = var.bucket_name
  location                    = var.region
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      with_state = "ANY"
      days_since_noncurrent_time = 7 
    }
  }
  
  depends_on = [google_project_service.gcp_apis]
}

# Creación del dataset de BigQuery
# Utilizado para almacenar datos estructurados, logs o resultados de predicciones.
resource "google_bigquery_dataset" "ml_dataset" {
  project    = var.project_id
  dataset_id = var.bq_dataset_name
  location   = var.region
  
  depends_on = [google_project_service.gcp_apis]
}