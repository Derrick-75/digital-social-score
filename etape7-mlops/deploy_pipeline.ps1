# Script pour deployer le pipeline depuis Cloud Shell

Write-Host "================================================"
Write-Host "Upload et lancement du pipeline MLOps"
Write-Host "================================================"

# Copier les fichiers vers Cloud Shell (via gcloud storage)
Write-Host "`nUpload des fichiers vers GCS..."
gsutil cp vertex_pipelines/ml_pipeline_clean.json gs://digitalsocialscoreapi_cloudbuild/mlops/
gsutil cp launch_pipeline_clean.py gs://digitalsocialscoreapi_cloudbuild/mlops/

Write-Host "`nFichiers uploadés. Maintenant, dans Cloud Shell, exécutez:"
Write-Host ""
Write-Host "gsutil cp gs://digitalsocialscoreapi_cloudbuild/mlops/launch_pipeline_clean.py ."
Write-Host "gsutil cp gs://digitalsocialscoreapi_cloudbuild/mlops/ml_pipeline_clean.json vertex_pipelines/"
Write-Host "python3 launch_pipeline_clean.py"
Write-Host ""
