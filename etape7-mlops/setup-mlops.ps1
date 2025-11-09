# Script PowerShell pour configurer l'environnement MLOps
# Usage: .\setup-mlops.ps1

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId = "digitalsocialscoreapi",
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "europe-west1"
)

Write-Host "🚀 Configuration de l'environnement MLOps..." -ForegroundColor Cyan
Write-Host "   Project: $ProjectId" -ForegroundColor Gray
Write-Host "   Region: $Region" -ForegroundColor Gray
Write-Host ""

# 1. Vérifier gcloud
Write-Host "1️⃣ Vérification de gcloud..." -ForegroundColor Yellow
$gcloudVersion = gcloud version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ gcloud CLI n'est pas installé" -ForegroundColor Red
    Write-Host "   Télécharger: https://cloud.google.com/sdk/docs/install" -ForegroundColor Gray
    exit 1
}
Write-Host "✅ gcloud CLI installé" -ForegroundColor Green

# 2. Configurer le projet
Write-Host ""
Write-Host "2️⃣ Configuration du projet..." -ForegroundColor Yellow
gcloud config set project $ProjectId
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Projet configuré: $ProjectId" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors de la configuration du projet" -ForegroundColor Red
    exit 1
}

# 3. Activer les APIs nécessaires
Write-Host ""
Write-Host "3️⃣ Activation des APIs GCP..." -ForegroundColor Yellow
$apis = @(
    "aiplatform.googleapis.com",
    "storage.googleapis.com",
    "cloudbuild.googleapis.com",
    "container.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "   Activation: $api" -ForegroundColor Gray
    gcloud services enable $api --project=$ProjectId 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ $api" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Erreur pour $api (peut-être déjà activée)" -ForegroundColor Yellow
    }
}

# 4. Créer/vérifier le bucket GCS
Write-Host ""
Write-Host "4️⃣ Configuration du bucket GCS..." -ForegroundColor Yellow
$bucketName = "${ProjectId}_cloudbuild"

$bucketExists = gsutil ls -b "gs://$bucketName" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Bucket existant: gs://$bucketName" -ForegroundColor Green
} else {
    Write-Host "   Création du bucket: gs://$bucketName" -ForegroundColor Gray
    gsutil mb -l $Region "gs://$bucketName"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Bucket créé: gs://$bucketName" -ForegroundColor Green
    } else {
        Write-Host "❌ Erreur lors de la création du bucket" -ForegroundColor Red
    }
}

# 5. Installer les dépendances Python
Write-Host ""
Write-Host "5️⃣ Installation des dépendances Python..." -ForegroundColor Yellow
$requirementsPath = "etape7-mlops\requirements.txt"
if (Test-Path $requirementsPath) {
    pip install -r $requirementsPath --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dépendances Python installées" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Erreur lors de l'installation des dépendances" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Fichier requirements.txt introuvable: $requirementsPath" -ForegroundColor Yellow
}

# 6. Vérifier les données d'entraînement
Write-Host ""
Write-Host "6️⃣ Vérification des données d'entraînement..." -ForegroundColor Yellow
$trainFile = "etape1-anonymisation\data\raw\train_advanced.csv"
$testFile = "etape1-anonymisation\data\raw\test_advanced.csv"

if (Test-Path $trainFile) {
    $trainSize = (Get-Item $trainFile).Length / 1MB
    Write-Host "✅ Train dataset: $trainFile ($([math]::Round($trainSize, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "❌ Train dataset introuvable: $trainFile" -ForegroundColor Red
}

if (Test-Path $testFile) {
    $testSize = (Get-Item $testFile).Length / 1MB
    Write-Host "✅ Test dataset: $testFile ($([math]::Round($testSize, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "❌ Test dataset introuvable: $testFile" -ForegroundColor Red
}

# Résumé
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Configuration MLOps terminée!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Prochaines étapes:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣ Uploader les données vers GCS:" -ForegroundColor White
Write-Host "   cd etape7-mlops" -ForegroundColor Gray
Write-Host "   python upload_data_to_gcs.py --project-id $ProjectId" -ForegroundColor Gray
Write-Host ""
Write-Host "2️⃣ Déclencher le pipeline MLOps:" -ForegroundColor White
Write-Host "   cd vertex_pipelines" -ForegroundColor Gray
Write-Host "   python trigger_pipeline.py --project-id $ProjectId --region $Region --model-type simple" -ForegroundColor Gray
Write-Host ""
Write-Host "3️⃣ Suivre l'exécution:" -ForegroundColor White
Write-Host "   https://console.cloud.google.com/vertex-ai/pipelines/runs?project=$ProjectId" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation: etape7-mlops\README.md" -ForegroundColor Cyan
Write-Host ""
