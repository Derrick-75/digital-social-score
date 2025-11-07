# Script de déploiement du monitoring Prometheus
# Digital Social Score API - Monitoring Setup

Write-Host "🚀 Configuration du Monitoring Prometheus pour Digital Social Score" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ID = "digitalsocialscoreapi"
$CLUSTER_NAME = "dss-cluster-autopilot"
$REGION = "europe-west1"
$NAMESPACE = "digital-social-score"

# Étape 1: Vérifier la connexion au cluster
Write-Host "📡 Étape 1/5: Connexion au cluster GKE..." -ForegroundColor Yellow
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION --project $PROJECT_ID

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur: Impossible de se connecter au cluster" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Connecté au cluster $CLUSTER_NAME" -ForegroundColor Green
Write-Host ""

# Étape 2: Activer les APIs nécessaires
Write-Host "🔧 Étape 2/5: Activation des APIs Google Cloud..." -ForegroundColor Yellow
$apis = @(
    "monitoring.googleapis.com",
    "cloudtrace.googleapis.com",
    "cloudprofiler.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "  - Activation de $api..." -ForegroundColor Gray
    gcloud services enable $api --project=$PROJECT_ID 2>$null
}
Write-Host "✅ APIs activées" -ForegroundColor Green
Write-Host ""

# Étape 3: Déployer PodMonitoring
Write-Host "📊 Étape 3/5: Déploiement du PodMonitoring resource..." -ForegroundColor Yellow
$podmonitoringPath = Join-Path $PSScriptRoot "..\etape3-api\k8s\podmonitoring.yaml"

if (Test-Path $podmonitoringPath) {
    kubectl apply -f $podmonitoringPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PodMonitoring déployé avec succès" -ForegroundColor Green
    } else {
        Write-Host "❌ Erreur lors du déploiement du PodMonitoring" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Fichier podmonitoring.yaml non trouvé: $podmonitoringPath" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Étape 4: Vérifier le déploiement
Write-Host "🔍 Étape 4/5: Vérification du déploiement..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

kubectl get podmonitoring -n $NAMESPACE
Write-Host ""

$podmonStatus = kubectl get podmonitoring dss-api-prometheus -n $NAMESPACE -o jsonpath='{.metadata.name}' 2>$null
if ($podmonStatus -eq "dss-api-prometheus") {
    Write-Host "✅ PodMonitoring actif et configuré" -ForegroundColor Green
} else {
    Write-Host "⚠️  PodMonitoring déployé mais vérification manuelle recommandée" -ForegroundColor Yellow
}
Write-Host ""

# Étape 5: Instructions finales
Write-Host "🎉 Étape 5/5: Configuration terminée!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Prochaines étapes:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Attendez 2-3 minutes que les métriques commencent à être collectées" -ForegroundColor White
Write-Host ""
Write-Host "2. Vérifiez que les métriques sont collectées:" -ForegroundColor White
Write-Host "   kubectl logs -n gmp-system -l app.kubernetes.io/name=operator --tail=20" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Créez votre dashboard Cloud Monitoring:" -ForegroundColor White
Write-Host "   https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID" -ForegroundColor Blue
Write-Host ""
Write-Host "4. Ou utilisez le script automatique de création de dashboard:" -ForegroundColor White
Write-Host "   .\create_monitoring_dashboard.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Lancez vos tests de charge avec Locust:" -ForegroundColor White
Write-Host "   cd etape5-load-testing" -ForegroundColor Gray
Write-Host "   locust -f locustfile.py --host=http://34.38.214.124" -ForegroundColor Gray
Write-Host ""
Write-Host "📊 Métriques Prometheus disponibles:" -ForegroundColor Cyan
Write-Host "   - toxicity_api_requests_total" -ForegroundColor White
Write-Host "   - toxicity_score_distribution" -ForegroundColor White
Write-Host "   - toxicity_processing_seconds" -ForegroundColor White
Write-Host "   - toxicity_api_active_users" -ForegroundColor White
Write-Host "   - model_load_seconds" -ForegroundColor White
Write-Host "   - + métriques HTTP et système" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Liens utiles:" -ForegroundColor Cyan
Write-Host "   Dashboard: https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID" -ForegroundColor Blue
Write-Host "   Metrics Explorer: https://console.cloud.google.com/monitoring/metrics-explorer?project=$PROJECT_ID" -ForegroundColor Blue
Write-Host "   Logs: https://console.cloud.google.com/logs?project=$PROJECT_ID" -ForegroundColor Blue
Write-Host ""
Write-Host "✨ Monitoring configuré avec succès! Bonne analyse!" -ForegroundColor Green
