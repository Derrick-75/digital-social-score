# Script pour lancer un test de charge de 5 minutes et voir le dashboard en action
# Usage: .\lancer_test_dashboard.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 TEST DE CHARGE - DASHBOARD MONITORING" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📊 Dashboard URL:" -ForegroundColor Yellow
Write-Host "https://console.cloud.google.com/monitoring/dashboards?project=digitalsocialscoreapi" -ForegroundColor Cyan
Write-Host ""

Write-Host "⏱️  Durée du test: 5 minutes" -ForegroundColor Yellow
Write-Host "👥 Utilisateurs simulés: 50" -ForegroundColor Yellow
Write-Host "📈 Spawn rate: 10 users/sec" -ForegroundColor Yellow
Write-Host ""

Write-Host "💡 Conseils:" -ForegroundColor Green
Write-Host "  1. Ouvrez le dashboard dans votre navigateur" -ForegroundColor White
Write-Host "  2. Rafraîchissez le dashboard toutes les 30 secondes" -ForegroundColor White
Write-Host "  3. Observez les graphiques se remplir en temps réel" -ForegroundColor White
Write-Host "  4. Prenez des captures d'écran pendant le test" -ForegroundColor White
Write-Host ""

Read-Host "Appuyez sur Entrée pour démarrer le test (ou Ctrl+C pour annuler)"

Write-Host ""
Write-Host "🔥 Démarrage du test de charge..." -ForegroundColor Green
Write-Host ""

# Lancer Locust
locust -f locustfile.py `
    --host=http://34.38.214.124 `
    --users 50 `
    --spawn-rate 10 `
    --run-time 5m `
    --headless `
    --html test_dashboard_5min.html `
    --csv test_dashboard_5min

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ TEST TERMINÉ !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "📊 Rapports générés:" -ForegroundColor Yellow
Write-Host "  - test_dashboard_5min.html (rapport HTML)" -ForegroundColor White
Write-Host "  - test_dashboard_5min_stats.csv (statistiques)" -ForegroundColor White
Write-Host "  - test_dashboard_5min_failures.csv (erreurs)" -ForegroundColor White
Write-Host ""

Write-Host "📸 N'oubliez pas de:" -ForegroundColor Cyan
Write-Host "  1. Prendre des captures du dashboard" -ForegroundColor White
Write-Host "  2. Noter les valeurs max/min/moyenne" -ForegroundColor White
Write-Host "  3. Ouvrir le rapport HTML: test_dashboard_5min.html" -ForegroundColor White
Write-Host ""

# Ouvrir le rapport
Write-Host "Ouverture du rapport..." -ForegroundColor Cyan
Start-Process "test_dashboard_5min.html"

Write-Host ""
Write-Host "🎯 Métriques attendues:" -ForegroundColor Yellow
Write-Host "  - Requêtes totales: ~15,000" -ForegroundColor White
Write-Host "  - Débit: ~50 req/s" -ForegroundColor White
Write-Host "  - Latence P50: < 50ms" -ForegroundColor White
Write-Host "  - Latence P95: < 200ms" -ForegroundColor White
Write-Host "  - Taux d'erreur: < 1%" -ForegroundColor White
Write-Host ""
