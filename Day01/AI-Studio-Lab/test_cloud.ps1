$ErrorActionPreference = "Stop"

$tfvarsFile = "terraform/terraform.tfvars"

if (-not (Test-Path $tfvarsFile)) {
    Write-Error "ERROR: terraform/terraform.tfvars file not found!"
    exit 1
}

$tfvarsContent = Get-Content $tfvarsFile
$projectId = $null
$bucketName = $null
$datasetId = "document_processing"
$tableId = "processed_metadata"

foreach ($line in $tfvarsContent) {
    if ($line -match '^\s*project_id\s*=\s*"(.*)"') {
        $projectId = $Matches[1]
    }
    elseif ($line -match '^\s*bucket_name\s*=\s*"(.*)"') {
        $bucketName = $Matches[1]
    }
    elseif ($line -match '^\s*dataset_id\s*=\s*"(.*)"') {
        $datasetId = $Matches[1]
    }
    elseif ($line -match '^\s*table_id\s*=\s*"(.*)"') {
        $tableId = $Matches[1]
    }
}

if (-not $projectId -or -not $bucketName) {
    Write-Error "ERROR: Could not parse project_id or bucket_name from $tfvarsFile."
    exit 1
}

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Live GCP Pipeline Validation Tool (PowerShell)" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Project ID:      $projectId"
Write-Host "Bucket Name:     $bucketName"
Write-Host "BigQuery Table:  $datasetId.$tableId"
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

$timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$testFile = "live_test_$timestamp.txt"

$testContent = @"
This is a live test document for validating the serverless event-driven document processing pipeline.
It contains key terms like pipeline serverless bigquery testing automated workflow.
"@

Set-Content -Path $testFile -Value $testContent

Write-Host "[1/4] Uploading test file to GCS: gs://$bucketName/$testFile..." -ForegroundColor Yellow
gcloud storage cp $testFile "gs://$bucketName/$testFile"

Write-Host "[2/4] Waiting 12 seconds for processing to propagate..." -ForegroundColor Yellow
Start-Sleep -Seconds 12

Write-Host "[3/4] Querying BigQuery dataset for metadata..." -ForegroundColor Yellow
$query = "SELECT filename, date, tags, word_count FROM ``$projectId.$datasetId.$tableId`` WHERE filename = '$testFile' LIMIT 1"

bq query --use_legacy_sql=false --project_id=$projectId $query

Write-Host "[4/4] Cleaning up test file..." -ForegroundColor Yellow
gcloud storage rm "gs://$bucketName/$testFile"
Remove-Item -Path $testFile -Force

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "Live test execution completed!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
