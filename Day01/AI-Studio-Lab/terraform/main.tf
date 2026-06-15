terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Enable Required GCP APIs
resource "google_project_service" "gcp_services" {
  for_each = toset([
    "run.googleapis.com",
    "pubsub.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "iam.googleapis.com"
  ])
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

# Get current project metadata (specifically for project number)
data "google_project" "project" {
  project_id = var.project_id
  depends_on = [google_project_service.gcp_services]
}

# 2. Cloud Storage Ingestion Bucket
resource "google_storage_bucket" "ingestion_bucket" {
  name                        = var.bucket_name
  location                    = var.region
  project                     = var.project_id
  force_destroy               = true # Set to true to allow cleanup of files during bucket deletion
  uniform_bucket_level_access = true

  depends_on = [google_project_service.gcp_services]
}

# 3. Pub/Sub Topic for GCS Notifications
resource "google_pubsub_topic" "gcs_notifications_topic" {
  name    = "gcs-upload-topic"
  project = var.project_id

  depends_on = [google_project_service.gcp_services]
}

# Get GCS System Service Account email to grant Pub/Sub publisher permissions
data "google_storage_project_service_account" "gcs_account" {
  project    = var.project_id
  depends_on = [google_project_service.gcp_services]
}

# Grant GCS service account permission to publish to the Pub/Sub Topic
resource "google_pubsub_topic_iam_member" "gcs_publisher" {
  topic      = google_pubsub_topic.gcs_notifications_topic.name
  role       = "roles/pubsub.publisher"
  member     = "serviceAccount:${data.google_storage_project_service_account.gcs_account.email_address}"
  depends_on = [google_pubsub_topic.gcs_notifications_topic]
}

# 4. GCS Bucket Notification Configuration
resource "google_storage_notification" "gcs_notification" {
  bucket         = google_storage_bucket.ingestion_bucket.name
  payload_format = "JSON_API_V1"
  topic          = google_pubsub_topic.gcs_notifications_topic.id
  event_types    = ["OBJECT_FINALIZE"]

  depends_on = [
    google_pubsub_topic_iam_member.gcs_publisher,
    google_storage_bucket.ingestion_bucket
  ]
}

# 5. BigQuery Dataset & Table
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.dataset_id
  project    = var.project_id
  location   = var.region

  depends_on = [google_project_service.gcp_services]
}

resource "google_bigquery_table" "table" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = var.table_id
  project    = var.project_id

  schema = jsonencode([
    {
      name        = "filename"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Name of the processed file"
    },
    {
      name        = "date"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "OCR processing completion timestamp"
    },
    {
      name        = "tags"
      type        = "STRING"
      mode        = "REPEATED"
      description = "Tags extracted from simulated OCR"
    },
    {
      name        = "word_count"
      type        = "INTEGER"
      mode        = "REQUIRED"
      description = "Word count of the document content"
    }
  ])

  depends_on = [google_bigquery_dataset.dataset]
}

# 6. Service Account for Cloud Run
resource "google_service_account" "cloud_run_sa" {
  account_id   = "document-processor-sa"
  display_name = "Cloud Run Document Processor Service Account"
  project      = var.project_id
  depends_on   = [google_project_service.gcp_services]
}

# IAM permissions for Cloud Run Service Account
resource "google_storage_bucket_iam_member" "cr_gcs_viewer" {
  bucket     = google_storage_bucket.ingestion_bucket.name
  role       = "roles/storage.objectViewer"
  member     = "serviceAccount:${google_service_account.cloud_run_sa.email}"
  depends_on = [google_storage_bucket.ingestion_bucket, google_service_account.cloud_run_sa]
}

resource "google_bigquery_dataset_iam_member" "cr_bq_editor" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.cloud_run_sa.email}"
  depends_on = [google_bigquery_dataset.dataset, google_service_account.cloud_run_sa]
}

# 7. Cloud Run Service (deployed using the container_image variable)
resource "google_cloud_run_v2_service" "processor" {
  name     = var.cloud_run_service_name
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.cloud_run_sa.email
    containers {
      image = var.container_image
      
      env {
        name  = "GCP_PROJECT"
        value = var.project_id
      }
      env {
        name  = "BQ_DATASET"
        value = google_bigquery_dataset.dataset.dataset_id
      }
      env {
        name  = "BQ_TABLE"
        value = google_bigquery_table.table.table_id
      }
    }
  }

  depends_on = [
    google_project_service.gcp_services,
    google_service_account.cloud_run_sa,
    google_bigquery_table.table
  ]
}

# 8. Service Account for Pub/Sub Subscription Invoker
resource "google_service_account" "pubsub_invoker" {
  account_id   = "pubsub-invoker-sa"
  display_name = "Pub/Sub Invoker Service Account"
  project      = var.project_id
  depends_on   = [google_project_service.gcp_services]
}

# Grant the Pub/Sub invoker service account permission to call the Cloud Run service
resource "google_cloud_run_v2_service_iam_member" "pubsub_invoker_member" {
  project    = google_cloud_run_v2_service.processor.project
  location   = google_cloud_run_v2_service.processor.location
  name       = google_cloud_run_v2_service.processor.name
  role       = "roles/run.invoker"
  member     = "serviceAccount:${google_service_account.pubsub_invoker.email}"
  depends_on = [google_cloud_run_v2_service.processor, google_service_account.pubsub_invoker]
}

# Grant Pub/Sub Service Identity permission to create OIDC tokens
# This is required for Pub/Sub to sign the push request using our invoker service account.
resource "google_project_iam_member" "pubsub_token_creator" {
  project    = var.project_id
  role       = "roles/iam.serviceAccountTokenCreator"
  member     = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
  depends_on = [data.google_project.project]
}

# 9. Pub/Sub Push Subscription to invoke Cloud Run
resource "google_pubsub_subscription" "cloud_run_push" {
  name    = "cloud-run-push-sub"
  topic   = google_pubsub_topic.gcs_notifications_topic.name
  project = var.project_id

  push_config {
    # Send the notifications to the FastAPI webhook endpoint on Cloud Run
    push_endpoint = "${google_cloud_run_v2_service.processor.uri}/webhook"

    oidc_token {
      service_account_email = google_service_account.pubsub_invoker.email
      audience              = google_cloud_run_v2_service.processor.uri
    }
  }

  depends_on = [
    google_pubsub_topic.gcs_notifications_topic,
    google_cloud_run_v2_service.processor,
    google_service_account.pubsub_invoker,
    google_project_iam_member.pubsub_token_creator
  ]
}
