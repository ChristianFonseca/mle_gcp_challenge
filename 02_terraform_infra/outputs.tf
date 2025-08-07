# outputs.tf

output "gcs_bucket_name" {
  description = "El nombre del bucket de GCS creado."
  value       = google_storage_bucket.ml_bucket.url
}

output "bigquery_dataset_id" {
  description = "El ID completo del dataset de BigQuery creado."
  value       = google_bigquery_dataset.ml_dataset.id
}

output "vertex_service_account_email" {
  description = "El email de la cuenta de servicio creada para Vertex AI."
  value       = google_service_account.vertex_sa.email
}