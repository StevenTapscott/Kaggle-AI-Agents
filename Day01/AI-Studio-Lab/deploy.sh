#!/bin/bash
# Exit immediately if a command exits with a non-zero status
set -e

TFVARS_FILE="terraform/terraform.tfvars"

# Check if terraform.tfvars exists
if [ ! -f "$TFVARS_FILE" ]; then
    echo "========================================================================="
    echo "ERROR: terraform/terraform.tfvars file not found!"
    echo "========================================================================="
    echo "Please copy terraform/terraform.tfvars.example to terraform/terraform.tfvars"
    echo "and edit it with your GCP Project ID, Bucket Name, and Container Image URI."
    echo ""
    echo "Example command:"
    echo "cp terraform/terraform.tfvars.example terraform/terraform.tfvars"
    echo "========================================================================="
    exit 1
fi

# Extract variables from tfvars file (removing whitespace and quotes)
PROJECT_ID=$(grep -E '^\s*project_id\s*=' "$TFVARS_FILE" | cut -d'=' -f2 | tr -d '[:space:]"')
REGION=$(grep -E '^\s*region\s*=' "$TFVARS_FILE" | cut -d'=' -f2 | tr -d '[:space:]"')
IMAGE_URI=$(grep -E '^\s*container_image\s*=' "$TFVARS_FILE" | cut -d'=' -f2 | tr -d '[:space:]"')

if [ -z "$PROJECT_ID" ] || [ -z "$REGION" ] || [ -z "$IMAGE_URI" ]; then
    echo "ERROR: Could not parse project_id, region, or container_image from $TFVARS_FILE."
    echo "Please make sure they are properly formatted (e.g., project_id = \"my-project-id\")."
    exit 1
fi

# Fallback to mock_bin if required CLIs are not installed
if ! command -v gcloud &> /dev/null || ! command -v docker &> /dev/null || ! command -v terraform &> /dev/null; then
    echo "========================================================================="
    echo "WARNING: Real gcloud, docker, or terraform CLI not found on PATH."
    echo "Using mock_bin simulation mode."
    echo "========================================================================="
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    export PATH="$SCRIPT_DIR/mock_bin:$PATH"
fi

echo "============================================="
echo "Pipeline Deployment Script"
echo "============================================="
echo "Project ID:      $PROJECT_ID"
echo "Region:          $REGION"
echo "Container Image: $IMAGE_URI"
echo "============================================="
echo ""

# Extract registry host name (e.g. us-central1-docker.pkg.dev)
REGISTRY=$(echo "$IMAGE_URI" | cut -d'/' -f1)

echo "[1/4] Configuring Docker authentication for $REGISTRY..."
gcloud auth configure-docker "$REGISTRY" --quiet

echo "[2/4] Building Docker container..."
docker build -t "$IMAGE_URI" ./src

echo "[3/4] Pushing container to Artifact Registry..."
docker push "$IMAGE_URI"

echo "[4/4] Deploying infrastructure via Terraform..."
cd terraform
terraform init
terraform apply -auto-approve

echo ""
echo "============================================="
echo "SUCCESS: Deployment complete!"
echo "============================================="
