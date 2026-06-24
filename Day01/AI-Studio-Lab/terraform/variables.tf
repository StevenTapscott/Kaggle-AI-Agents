variable "project_id" {
  description = "The GCP Project ID where resources will be provisioned."
  type        = string
}

variable "region" {
  description = "The region to provision resources (e.g., us-central1)."
  type        = string
  default     = "us-central1"
}

variable "bucket_name" {
  description = "The name of the GCS bucket for document uploads. Must be globally unique."
  type        = string
}

variable "dataset_id" {
  description = "The BigQuery dataset ID for storing document metadata."
  type        = string
  default     = "document_processing"
}

variable "table_id" {
  description = "The BigQuery table ID."
  type        = string
  default     = "processed_metadata"
}

variable "cloud_run_service_name" {
  description = "The name of the Cloud Run service."
  type        = string
  default     = "document-processor"
}

variable "container_image" {
  description = "The container image URI to deploy to Cloud Run (e.g., us-central1-docker.pkg.dev/my-project/my-repo/my-image:latest)."
  type        = string
}
