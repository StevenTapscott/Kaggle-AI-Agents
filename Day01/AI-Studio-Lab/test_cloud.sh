#!/bin/bash
set -e

TFVARS_FILE="terraform/terraform.tfvars"

# Check if terraform.tfvars exists
if [ ! -f "$TFVARS_FILE" ]; then
    echo "ERROR: terraform/terraform.tfvars file not found!"
    exit 1
fi

# Extract variables from tfvars file
PROJECT_ID=$(grep -E '^\s*project_id\s*=' "$TFVARS_FILE" | cut -d'=' -f2 | tr -d '[:space:]"')
BUCKET_NAME=$(grep -E '^\s*bucket_name\s*=' "$TFVARS_FILE" | cut -d'=' -f2 | tr -d '[:space:]"')
DATASET_ID=$(grep -E '^\s*dataset_id\s*=' "$TFVARS_FILE" | cut -d'=' -f2 | tr -d '[:space:]"')
TABLE_ID=$(grep -E '^\s*table_id\s*=' "$TFVARS_FILE" | cut -d'=' -f2 | tr -d '[:space:]"')

if [ -z "$PROJECT_ID" ] || [ -z "$BUCKET_NAME" ] || [ -z "$DATASET_ID" ] || [ -z "$TABLE_ID" ]; then
    echo "ERROR: Could not parse project_id, bucket_name, dataset_id, or table_id from $TFVARS_FILE."
    exit 1
fi

# Fallback to mock_bin if required CLIs are not installed
if ! command -v gcloud &> /dev/null || ! command -v bq &> /dev/null; then
    echo "========================================================================="
    echo "WARNING: Real gcloud or bq CLI not found on PATH."
    echo "Using mock_bin simulation mode."
    echo "========================================================================="
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    export PATH="$SCRIPT_DIR/mock_bin:$PATH"
fi

echo "============================================="
echo "Live GCP Pipeline Validation Tool"
echo "============================================="
echo "Project ID:      $PROJECT_ID"
echo "Bucket Name:     $BUCKET_NAME"
echo "BigQuery Table:  $DATASET_ID.$TABLE_ID"
echo "============================================="
echo ""

# 1. Create a dummy test file
TEST_FILE="live_test_$(date +%s).txt"
echo "This is a live test document for validating the serverless event-driven document processing pipeline." > "$TEST_FILE"
echo "It contains key terms like pipeline serverless bigquery testing automated workflow." >> "$TEST_FILE"

echo "[1/4] Uploading test file to GCS: gs://$BUCKET_NAME/$TEST_FILE..."
gcloud storage cp "$TEST_FILE" "gs://$BUCKET_NAME/$TEST_FILE"

echo "[2/4] Waiting 12 seconds for processing to propagate..."
sleep 12

echo "[3/4] Querying BigQuery dataset for metadata..."
QUERY="SELECT filename, date, tags, word_count FROM \`$PROJECT_ID.$DATASET_ID.$TABLE_ID\` WHERE filename = '$TEST_FILE' LIMIT 1"

# Run BQ query
bq query --use_legacy_sql=false --project_id="$PROJECT_ID" "$QUERY"

echo "[4/4] Cleaning up test file..."
gcloud storage rm "gs://$BUCKET_NAME/$TEST_FILE"
rm "$TEST_FILE"

echo ""
echo "============================================="
echo "Live test execution completed!"
echo "============================================="
