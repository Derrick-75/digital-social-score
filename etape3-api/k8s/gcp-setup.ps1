# Script de Configuration GCP pour Digital Social Score API
# Prérequis : gcloud CLI installé et configuré

param(
    [string]$ProjectId = "",
    [string]$ClusterName = "dss-cluster",
    [string]$Zone = "europe-west1-b",
    [string]$NodeCount = "2"
)

Write-Host "🌐 Configuration GCP pour Digital Social Score API" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Vérification des prérequis
Write-Host "`n1️⃣ Vérification des prérequis..." -ForegroundColor Yellow

# Vérifier gcloud CLI
try {
    $gcloudVersion = gcloud version 2>$null
    Write-Host "✅ Google Cloud CLI installé" -ForegroundColor Green
} catch {
    Write-Host "❌ Google Cloud CLI non trouvé. Installez-le depuis: https://cloud.google.com/sdk/docs/install" -ForegroundColor Red
    exit 1
}

# Vérifier kubectl
try {
    $kubectlVersion = kubectl version --client 2>$null
    Write-Host "✅ kubectl installé" -ForegroundColor Green
} catch {
    Write-Host "❌ kubectl non trouvé. Installation..." -ForegroundColor Yellow
    gcloud components install kubectl
}

# Vérifier Docker
try {
    $dockerVersion = docker --version 2>$null
    Write-Host "✅ Docker installé" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker non trouvé. Installez Docker Desktop" -ForegroundColor Red
    exit 1
}

# Configuration du projet
if (-not $ProjectId) {
    Write-Host "`n2️⃣ Configuration du projet GCP..." -ForegroundColor Yellow
    $ProjectId = Read-Host "Entrez votre Project ID GCP"
}

Write-Host "Configuration du projet: $ProjectId" -ForegroundColor Blue
gcloud config set project $ProjectId

# Activation des APIs nécessaires
Write-Host "`n3️⃣ Activation des APIs GCP..." -ForegroundColor Yellow
$apis = @(
    "container.googleapis.com",
    "containerregistry.googleapis.com",
    "cloudbuild.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "Activation de $api..." -ForegroundColor Blue
    gcloud services enable $api
}

# Création du cluster GKE
Write-Host "`n4️⃣ Création du cluster GKE..." -ForegroundColor Yellow
Write-Host "Nom du cluster: $ClusterName" -ForegroundColor Blue
Write-Host "Zone: $Zone" -ForegroundColor Blue
Write-Host "Nombre de nœuds: $NodeCount" -ForegroundColor Blue

$clusterExists = gcloud container clusters describe $ClusterName --zone=$Zone 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "⚠️ Le cluster $ClusterName existe déjà" -ForegroundColor Yellow
    $recreate = Read-Host "Voulez-vous le recréer? (y/N)"
    if ($recreate -eq "y" -or $recreate -eq "Y") {
        Write-Host "Suppression du cluster existant..." -ForegroundColor Yellow
        gcloud container clusters delete $ClusterName --zone=$Zone --quiet
    } else {
        Write-Host "Utilisation du cluster existant" -ForegroundColor Green
        gcloud container clusters get-credentials $ClusterName --zone=$Zone
        kubectl config current-context
        Write-Host "`n✅ Prêt pour le déploiement!" -ForegroundColor Green
        Write-Host "Exécutez maintenant: .\deploy-gcp.ps1" -ForegroundColor Cyan
        exit 0
    }
}

Write-Host "Création du cluster GKE (cela peut prendre 5-10 minutes)..." -ForegroundColor Blue
gcloud container clusters create $ClusterName `
    --zone=$Zone `
    --num-nodes=$NodeCount `
    --enable-autoscaling `
    --min-nodes=1 `
    --max-nodes=5 `
    --machine-type=e2-medium `
    --disk-size=20GB `
    --enable-autorepair `
    --enable-autoupgrade

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de la création du cluster" -ForegroundColor Red
    exit 1
}

# Configuration de kubectl
Write-Host "`n5️⃣ Configuration de kubectl..." -ForegroundColor Yellow
gcloud container clusters get-credentials $ClusterName --zone=$Zone

# Vérification
Write-Host "`n6️⃣ Vérification du cluster..." -ForegroundColor Yellow
kubectl cluster-info
kubectl get nodes

# Création d'une adresse IP statique pour le LoadBalancer (optionnel)
Write-Host "`n7️⃣ Création d'une adresse IP statique..." -ForegroundColor Yellow
$createStaticIP = Read-Host "Créer une adresse IP statique pour le LoadBalancer? (y/N)"
if ($createStaticIP -eq "y" -or $createStaticIP -eq "Y") {
    Write-Host "Création de l'adresse IP statique..." -ForegroundColor Blue
    gcloud compute addresses create dss-api-ip --global
    
    $staticIP = gcloud compute addresses describe dss-api-ip --global --format="value(address)"
    Write-Host "✅ Adresse IP statique créée: $staticIP" -ForegroundColor Green
}

# Installation du metrics server si nécessaire
Write-Host "`n8️⃣ Installation du metrics server..." -ForegroundColor Yellow
$metricsDeployed = kubectl get deployment metrics-server -n kube-system 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installation du metrics server pour l'autoscaling..." -ForegroundColor Blue
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    
    # Patch pour GKE (résolution de noms)
    kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
    
    Write-Host "✅ Metrics server installé" -ForegroundColor Green
} else {
    Write-Host "✅ Metrics server déjà installé" -ForegroundColor Green
}

# Configuration des quotas recommandés
Write-Host "`n9️⃣ Vérification des quotas..." -ForegroundColor Yellow
Write-Host "Vérification des quotas GCP pour éviter les problèmes..." -ForegroundColor Blue

$quotas = gcloud compute project-info describe --project=$ProjectId --format="value(quotas[].metric,quotas[].limit)" 2>$null
if ($quotas) {
    Write-Host "✅ Quotas vérifiés" -ForegroundColor Green
    Write-Host "⚠️ Surveillez les quotas CPUS, IN_USE_ADDRESSES, STATIC_ADDRESSES" -ForegroundColor Yellow
} else {
    Write-Host "⚠️ Impossible de vérifier les quotas" -ForegroundColor Yellow
}

Write-Host "`n✅ Configuration GCP terminée avec succès!" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host "Cluster GKE: $ClusterName" -ForegroundColor Cyan
Write-Host "Zone: $Zone" -ForegroundColor Cyan
Write-Host "Projet: $ProjectId" -ForegroundColor Cyan
Write-Host "Contexte kubectl configuré" -ForegroundColor Cyan

if ($staticIP) {
    Write-Host "IP statique: $staticIP" -ForegroundColor Cyan
}

Write-Host "`n🎯 Prochaines étapes:" -ForegroundColor Yellow
Write-Host "1. .\deploy-gcp.ps1 -ProjectId $ProjectId" -ForegroundColor White
Write-Host "2. .\monitor-gcp.ps1 (pour surveiller)" -ForegroundColor White
Write-Host "3. Consulter GCP-DEPLOYMENT-GUIDE.md pour plus de détails" -ForegroundColor White

Write-Host "`n📋 Commandes utiles:" -ForegroundColor Yellow
Write-Host "kubectl get nodes" -ForegroundColor White
Write-Host "kubectl cluster-info" -ForegroundColor White
Write-Host "gcloud container clusters list" -ForegroundColor White
