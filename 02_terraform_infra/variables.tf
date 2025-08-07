# variables.tf

variable "project_id" {
  description = "El ID del proyecto de GCP donde se desplegarán los recursos."
  type        = string
}

variable "region" {
  description = "La región de GCP para los recursos."
  type        = string
  default     = "us-central1"
}

variable "bucket_name" {
  description = "El nombre para el bucket de GCS. Debe ser globalmente único."
  type        = string
}

variable "bq_dataset_name" {
  description = "El nombre para el dataset de BigQuery."
  type        = string
  default     = "mlops_churn_dataset"
}

variable "service_account_id" {
  description = "El ID para la cuenta de servicio que ejecutará los pipelines."
  type        = string
  default     = "vertex-pipeline-runner"
}