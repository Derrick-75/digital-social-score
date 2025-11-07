# Script de vérification AVANT de push sur GitHub
# Usage: .\pre-push-check.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔍 VÉRIFICATION PRÉ-PUSH" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$errors = 0
$warnings = 0

# ========================================
# 1. Vérifier qu'il n'y a pas de secrets
# ========================================
Write-Host "1️⃣ Recherche de secrets/credentials..." -ForegroundColor Yellow

$secretPatterns = @(
    "*.key",
    "*.pem",
    "credentials.json",
    ".env",
    "*password*",
    "*secret*",
    "*token*"
)

foreach ($pattern in $secretPatterns) {
    $files = git ls-files | Select-String -Pattern $pattern -SimpleMatch
    if ($files) {
        Write-Host "   ❌ ERREUR: Fichiers secrets détectés:" -ForegroundColor Red
        $files | ForEach-Object { Write-Host "      - $_" -ForegroundColor Red }
        $errors++
    }
}

if ($errors -eq 0) {
    Write-Host "   ✅ Aucun secret détecté" -ForegroundColor Green
}

# ========================================
# 2. Vérifier les fichiers de données (RGPD)
# ========================================
Write-Host ""
Write-Host "2️⃣ Vérification RGPD (données personnelles)..." -ForegroundColor Yellow

$dataFiles = git ls-files | Where-Object { 
    $_ -match "\.csv$" -or 
    $_ -match "data/raw/" -or
    $_ -match "data/train" 
}

if ($dataFiles) {
    Write-Host "   ⚠️  ATTENTION: Fichiers de données détectés:" -ForegroundColor Yellow
    $dataFiles | ForEach-Object { Write-Host "      - $_" -ForegroundColor Yellow }
    Write-Host "   ℹ️  Vérifiez qu'ils sont bien anonymisés!" -ForegroundColor Cyan
    $warnings++
} else {
    Write-Host "   ✅ Aucun fichier de données brutes" -ForegroundColor Green
}

# ========================================
# 3. Vérifier les modèles lourds
# ========================================
Write-Host ""
Write-Host "3️⃣ Vérification des modèles (taille)..." -ForegroundColor Yellow

$modelFiles = git ls-files | Where-Object { 
    $_ -match "\.(h5|pkl|bin|safetensors)$" 
}

if ($modelFiles) {
    Write-Host "   ⚠️  ATTENTION: Modèles détectés (peuvent être lourds):" -ForegroundColor Yellow
    foreach ($file in $modelFiles) {
        if (Test-Path $file) {
            $size = (Get-Item $file).Length / 1MB
            $color = if ($size -gt 100) { "Red" } elseif ($size -gt 10) { "Yellow" } else { "Green" }
            Write-Host "      - $file (${size:N2} MB)" -ForegroundColor $color
            if ($size -gt 100) {
                $errors++
            }
        }
    }
} else {
    Write-Host "   ✅ Aucun modèle lourd détecté" -ForegroundColor Green
}

# ========================================
# 4. Vérifier que cloudbuild.yaml est présent
# ========================================
Write-Host ""
Write-Host "4️⃣ Vérification Cloud Build..." -ForegroundColor Yellow

if (Test-Path "cloudbuild.yaml") {
    Write-Host "   ✅ cloudbuild.yaml présent" -ForegroundColor Green
} else {
    Write-Host "   ❌ cloudbuild.yaml MANQUANT!" -ForegroundColor Red
    $errors++
}

# ========================================
# 5. Vérifier les fichiers tests
# ========================================
Write-Host ""
Write-Host "5️⃣ Vérification des rapports de tests..." -ForegroundColor Yellow

$testReports = git ls-files | Where-Object { 
    $_ -match "test.*\.html$" -or 
    $_ -match "test.*\.csv$" 
}

if ($testReports) {
    Write-Host "   ⚠️  Rapports de tests détectés (peuvent être lourds):" -ForegroundColor Yellow
    $testReports | ForEach-Object { Write-Host "      - $_" -ForegroundColor Yellow }
    $warnings++
} else {
    Write-Host "   ✅ Aucun rapport de test (bien, ils sont dans .gitignore)" -ForegroundColor Green
}

# ========================================
# 6. Vérifier les fichiers README
# ========================================
Write-Host ""
Write-Host "6️⃣ Vérification de la documentation..." -ForegroundColor Yellow

$readmes = git ls-files | Where-Object { $_ -match "README\.md$" }
$readmeCount = ($readmes | Measure-Object).Count

if ($readmeCount -ge 5) {
    Write-Host "   ✅ $readmeCount README trouvés (bonne documentation!)" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Seulement $readmeCount README trouvés" -ForegroundColor Yellow
    $warnings++
}

# ========================================
# 7. Vérifier la structure du projet
# ========================================
Write-Host ""
Write-Host "7️⃣ Vérification de la structure du projet..." -ForegroundColor Yellow

$requiredDirs = @(
    "etape1-anonymisation",
    "etape2-modele-ia",
    "etape3-api",
    "etape5-load-testing",
    "etape7-cloud-build"
)

$missingDirs = @()
foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        $missingDirs += $dir
    }
}

if ($missingDirs.Count -eq 0) {
    Write-Host "   ✅ Tous les dossiers essentiels présents" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Dossiers manquants:" -ForegroundColor Yellow
    $missingDirs | ForEach-Object { Write-Host "      - $_" -ForegroundColor Yellow }
    $warnings++
}

# ========================================
# RÉSUMÉ
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📊 RÉSUMÉ" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($errors -eq 0 -and $warnings -eq 0) {
    Write-Host "✅ Tout est OK! Vous pouvez push en toute sécurité!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Commandes à exécuter:" -ForegroundColor Cyan
    Write-Host "  git add ." -ForegroundColor White
    Write-Host "  git commit -m 'feat: Add Cloud Build CI/CD pipeline'" -ForegroundColor White
    Write-Host "  git push origin main" -ForegroundColor White
} elseif ($errors -eq 0) {
    Write-Host "⚠️  $warnings avertissement(s) détecté(s)" -ForegroundColor Yellow
    Write-Host "Vous pouvez continuer, mais vérifiez les points ci-dessus." -ForegroundColor Yellow
} else {
    Write-Host "❌ $errors erreur(s) détectée(s)!" -ForegroundColor Red
    Write-Host "❌ NE PUSH PAS avant de corriger ces erreurs!" -ForegroundColor Red
    exit 1
}

Write-Host ""
