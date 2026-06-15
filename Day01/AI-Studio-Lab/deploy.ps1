$ErrorActionPreference = "Stop"

$tfvarsFile = "terraform/terraform.tfvars"

# Check if terraform.tfvars exists
if (-not (Test-Path $tfvarsFile)) {
    Write-Host "=========================================================================" -ForegroundColor Red
    Write-Host "ERROR: terraform/terraform.tfvars file not found!" -ForegroundColor Red
    Write-Host "=========================================================================" -ForegroundColor Red
    Write-Host "Please copy terraform/terraform.tfvars.example to terraform/terraform.tfvars"
    Write-Host "and edit it with your GCP Project ID, Bucket Name, and Container Image URI."
    Write-Host ""
    Write-Host "Example command:"
    Write-Host "Copy-Item terraform/terraform.tfvars.example terraform/terraform.tfvars"
    Write-Host "========================================================================="
    exit 1
}

# Parse variables from tfvars file using regex
$tfvarsContent = Get-Content $tfvarsFile
$projectId = $null
$region = "us-central1"
$imageUri = $null

foreach ($line in $tfvarsContent) {
    if ($line -match '^\s*project_id\s*=\s*"(.*)"') {
        $projectId = $Matches[1]
    }
    elseif ($line -match '^\s*region\s*=\s*"(.*)"') {
        $region = $Matches[1]
    }
    elseif ($line -match '^\s*container_image\s*=\s*"(.*)"') {
        $imageUri = $Matches[1]
    }
}

if (-not $projectId -or -not $imageUri) {
    Write-Error "ERROR: Could not parse project_id or container_image from $tfvarsFile. Please make sure they are uncommented and correctly quoted."
    exit 1
}

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Pipeline Deployment Script (PowerShell)" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Project ID:      $projectId"
Write-Host "Region:          $region"
Write-Host "Container Image: $imageUri"
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

$registry = $imageUri.Split("/")[0]

Write-Host "[1/4] Configuring Docker authentication for $registry..." -ForegroundColor Yellow
gcloud auth configure-docker $registry --quiet

Write-Host "[2/4] Building Docker container..." -ForegroundColor Yellow
docker build -t $imageUri ./src

Write-Host "[3/4] Pushing container to Artifact Registry..." -ForegroundColor Yellow
docker push $imageUri

Write-Host "[4/4] Deploying infrastructure via Terraform..." -ForegroundColor Yellow
Push-Location terraform
try {
    terraform init
    terraform apply -auto-approve
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "SUCCESS: Deployment complete!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
