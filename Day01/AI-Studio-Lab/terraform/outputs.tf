output "bucket_name" {
  description = "The name of the GCS bucket."
  value       = google_storage_bucket.ingestion_bucket.name
}

output "pubsub_topic" {
  description = "The name of the Pub/Sub topic."
  value       = google_pubsub_topic.gcs_notifications_topic.name
}

output "cloud_run_url" {
  description = "The URL of the Cloud Run service."
  value       = google_cloud_run_v2_service.processor.uri
}

output "bigquery_table" {
  description = "The BigQuery table reference."
  value       = "${google_bigquery_dataset.dataset.dataset_id}.${google_bigquery_table.table.table_id}"
}
