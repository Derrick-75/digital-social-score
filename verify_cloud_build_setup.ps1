# Script de vérification de la configuration Cloud Build
# Usage: .\verify_cloud_build_setup.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔍 VÉRIFICATION CONFIGURATION CLOUD BUILD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$errors = 0

# ========================================
# 1. Vérifier que cloudbuild.yaml existe
# ========================================
Write-Host "📋 Étape 1/6: Vérification cloudbuild.yaml..." -ForegroundColor Yellow

if (Test-Path "cloudbuild.yaml") {
    Write-Host "  ✅ cloudbuild.yaml trouvé à la racine" -ForegroundColor Green
} else {
    Write-Host "  ❌ cloudbuild.yaml manquant!" -ForegroundColor Red
    $errors++
}

# ========================================
# 2. Vérifier la structure des fichiers
# ========================================
Write-Host ""
Write-Host "📁 Étape 2/6: Vérification de la structure..." -ForegroundColor Yellow

$requiredFiles = @(
    "etape3-api/Dockerfile",
    "etape3-api/requirements.txt",
    "etape3-api/tests/test_api.py",
    "etape3-api/app/main.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file manquant" -ForegroundColor Red
        $errors++
    }
}

# ========================================
# 3. Vérifier que gcloud est installé
# ========================================
Write-Host ""
Write-Host "☁️  Étape 3/6: Vérification gcloud CLI..." -ForegroundColor Yellow

try {
    $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
    Write-Host "  ✅ gcloud installé: $gcloudVersion" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  gcloud non installé ou non dans PATH" -ForegroundColor Yellow
    Write-Host "     Téléchargez: https://cloud.google.com/sdk/docs/install" -ForegroundColor White
}

# ========================================
# 4. Vérifier le projet GCP actuel
# ========================================
Write-Host ""
Write-Host "🏗️  Étape 4/6: Vérification projet GCP..." -ForegroundColor Yellow

try {
    $currentProject = gcloud config get-value project 2>$null
    
    if ($currentProject -eq "digitalsocialscoreapi") {
        Write-Host "  ✅ Projet correct: $currentProject" -ForegroundColor Green
    } elseif ($currentProject) {
        Write-Host "  ⚠️  Projet actuel: $currentProject" -ForegroundColor Yellow
        Write-Host "     Attendu: digitalsocialscoreapi" -ForegroundColor White
        Write-Host "     Commande: gcloud config set project digitalsocialscoreapi" -ForegroundColor Cyan
    } else {
        Write-Host "  ❌ Aucun projet configuré" -ForegroundColor Red
        $errors++
    }
} catch {
    Write-Host "  ⚠️  Impossible de vérifier le projet (gcloud non configuré)" -ForegroundColor Yellow
}

# ========================================
# 5. Vérifier que le cluster GKE existe
# ========================================
Write-Host ""
Write-Host "☸️  Étape 5/6: Vérification cluster GKE..." -ForegroundColor Yellow

try {
    $clusters = gcloud container clusters list --format="value(name)" --region=europe-west1 2>$null
    
    if ($clusters -contains "dss-cluster") {
        Write-Host "  ✅ Cluster GKE 'dss-cluster' trouvé" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Cluster 'dss-cluster' introuvable dans europe-west1" -ForegroundColor Red
        Write-Host "     Clusters disponibles: $clusters" -ForegroundColor White
        $errors++
    }
} catch {
    Write-Host "  ⚠️  Impossible de vérifier les clusters (vérifiez les permissions)" -ForegroundColor Yellow
}

# ========================================
# 6. Vérifier que Git est configuré
# ========================================
Write-Host ""
Write-Host "📦 Étape 6/6: Vérification Git..." -ForegroundColor Yellow

try {
    $gitRemote = git remote get-url origin 2>$null
    
    if ($gitRemote -like "*github.com*") {
        Write-Host "  ✅ Repository GitHub configuré: $gitRemote" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Remote non GitHub: $gitRemote" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ Pas de remote Git configuré" -ForegroundColor Red
    $errors++
}

# Vérifier s'il y a des fichiers non commités
$gitStatus = git status --short 2>$null
if ($gitStatus) {
    Write-Host "  ⚠️  Fichiers non commités détectés" -ForegroundColor Yellow
    Write-Host "     Pensez à commit/push avant de tester le pipeline" -ForegroundColor White
}

# ========================================
# RÉSUMÉ
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📊 RÉSUMÉ" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($errors -eq 0) {
    Write-Host "✅ Tous les prérequis sont satisfaits!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Prochaines étapes:" -ForegroundColor Yellow
    Write-Host "  1. Suivez le guide: GUIDE_CLOUD_BUILD.md" -ForegroundColor White
    Write-Host "  2. Activez Cloud Build API sur GCP" -ForegroundColor White
    Write-Host "  3. Connectez votre repository GitHub" -ForegroundColor White
    Write-Host "  4. Créez le déclencheur (trigger)" -ForegroundColor White
    Write-Host "  5. Faites un 'git push' pour tester!" -ForegroundColor White
} else {
    Write-Host "❌ $errors erreur(s) détectée(s)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Corrigez les erreurs ci-dessus avant de continuer" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📖 Documentation complète: GUIDE_CLOUD_BUILD.md" -ForegroundColor Cyan
Write-Host ""

# ========================================
# INFORMATIONS SUPPLÉMENTAIRES
# ========================================
Write-Host "📋 Informations de configuration:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Fichier de build: cloudbuild.yaml" -ForegroundColor White
Write-Host "  Projet GCP: digitalsocialscoreapi" -ForegroundColor White
Write-Host "  Cluster GKE: dss-cluster" -ForegroundColor White
Write-Host "  Région: europe-west1" -ForegroundColor White
Write-Host "  Namespace: dss" -ForegroundColor White
Write-Host "  IP API: 34.38.214.124" -ForegroundColor White
Write-Host ""

# ========================================
# COMMANDES UTILES
# ========================================
Write-Host "💡 Commandes utiles:" -ForegroundColor Green
Write-Host ""
Write-Host "  # Activer Cloud Build API" -ForegroundColor Cyan
Write-Host "  gcloud services enable cloudbuild.googleapis.com" -ForegroundColor White
Write-Host ""
Write-Host "  # Lister les triggers" -ForegroundColor Cyan
Write-Host "  gcloud builds triggers list" -ForegroundColor White
Write-Host ""
Write-Host "  # Voir l'historique des builds" -ForegroundColor Cyan
Write-Host "  gcloud builds list --limit=5" -ForegroundColor White
Write-Host ""
Write-Host "  # Tester le build localement (sans déploiement)" -ForegroundColor Cyan
Write-Host "  gcloud builds submit --config=cloudbuild.yaml ." -ForegroundColor White
Write-Host ""
