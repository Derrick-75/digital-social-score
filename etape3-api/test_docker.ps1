# Script PowerShell de test Docker pour l'API Digital Social Score

Write-Host "🐳 Test Docker - Digital Social Score API" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Vérifier que Docker fonctionne
Write-Host "🔍 Vérification de Docker..." -ForegroundColor Yellow
try {
    docker --version
    if ($LASTEXITCODE -ne 0) {
        throw "Docker command failed"
    }
    Write-Host "✅ Docker est disponible" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker n'est pas démarré" -ForegroundColor Red
    Write-Host "💡 Démarrez Docker Desktop et relancez ce script" -ForegroundColor Yellow
    exit 1
}

# Build de l'image
Write-Host ""
Write-Host "🏗️  Construction de l'image..." -ForegroundColor Yellow
docker build -t digital-social-score-api .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Image construite avec succès" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors de la construction" -ForegroundColor Red
    exit 1
}

# Afficher les informations
Write-Host ""
Write-Host "🚀 Pour démarrer le container:" -ForegroundColor Cyan
Write-Host "docker run -p 8000:8000 --name dss-api digital-social-score-api" -ForegroundColor White
Write-Host ""
Write-Host "📖 API sera disponible sur http://localhost:8000" -ForegroundColor Green
Write-Host "🛑 Appuyez sur Ctrl+C pour arrêter" -ForegroundColor Yellow

# Demander si on lance le container
$response = Read-Host "Lancer le container maintenant ? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "🚀 Démarrage du container..." -ForegroundColor Green
    docker run -p 8000:8000 --name dss-api digital-social-score-api
}
