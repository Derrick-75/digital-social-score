# Test de l'API déployée sur Kubernetes

param(
    [string]$BaseUrl = "http://localhost:8080",
    [int]$TimeoutSeconds = 30
)

Write-Host "🧪 Test de l'API Digital Social Score sur Kubernetes" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
Write-Host "URL de base: $BaseUrl"
Write-Host ""

# Fonction de test HTTP
function Test-ApiEndpoint {
    param(
        [string]$Endpoint,
        [string]$Method = "GET",
        [hashtable]$Body = $null,
        [string]$Description
    )
    
    Write-Host "🔍 Test: $Description" -ForegroundColor Yellow
    
    try {
        $headers = @{
            "Content-Type" = "application/json"
            "Accept" = "application/json"
        }
        
        $params = @{
            Uri = "$BaseUrl$Endpoint"
            Method = $Method
            Headers = $headers
            TimeoutSec = $TimeoutSeconds
        }
        
        if ($Body) {
            $params.Body = $Body | ConvertTo-Json
        }
        
        $response = Invoke-RestMethod @params
        Write-Host "   ✅ Status: OK" -ForegroundColor Green
        Write-Host "   📄 Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Cyan
        return $true
    }
    catch {
        Write-Host "   ❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Tests des endpoints
$testResults = @()

# 1. Health Check
$testResults += Test-ApiEndpoint -Endpoint "/health" -Description "Health Check"

# 2. API Info
$testResults += Test-ApiEndpoint -Endpoint "/models/info" -Description "Models Info"

# 3. Stats
$testResults += Test-ApiEndpoint -Endpoint "/stats" -Description "Statistics"

# 4. Documentation
$testResults += Test-ApiEndpoint -Endpoint "/docs" -Description "Documentation Swagger"

# 5. Analyse de texte (BERT)
$analyzeBody = @{
    text = "Ce message est très positif et bienveillant"
    model = "bert"
}
$testResults += Test-ApiEndpoint -Endpoint "/analyze" -Method "POST" -Body $analyzeBody -Description "Analyze (BERT - Positive)"

# 6. Analyse de texte (Simple)
$analyzeBody2 = @{
    text = "Tu es un idiot complet"
    model = "simple"
}
$testResults += Test-ApiEndpoint -Endpoint "/analyze" -Method "POST" -Body $analyzeBody2 -Description "Analyze (Simple - Toxic)"

# 7. Test avec texte neutre
$analyzeBody3 = @{
    text = "Bonjour, comment allez-vous aujourd'hui ?"
    model = "bert"
}
$testResults += Test-ApiEndpoint -Endpoint "/analyze" -Method "POST" -Body $analyzeBody3 -Description "Analyze (BERT - Neutral)"

# Résumé des tests
Write-Host ""
Write-Host "📊 RÉSUMÉ DES TESTS" -ForegroundColor Magenta
Write-Host "===================" -ForegroundColor Magenta

$successCount = ($testResults | Where-Object { $_ -eq $true }).Count
$totalCount = $testResults.Count
$successRate = [math]::Round(($successCount / $totalCount) * 100, 1)

Write-Host "Total des tests: $totalCount"
Write-Host "Tests réussis: $successCount"
Write-Host "Taux de réussite: $successRate%"

if ($successRate -eq 100) {
    Write-Host "🎉 Tous les tests sont passés avec succès!" -ForegroundColor Green
} elseif ($successRate -ge 80) {
    Write-Host "⚠️  La plupart des tests sont passés" -ForegroundColor Yellow
} else {
    Write-Host "❌ Plusieurs tests ont échoué" -ForegroundColor Red
}

# Test de charge basique
Write-Host ""
Write-Host "⚡ TEST DE CHARGE BASIQUE" -ForegroundColor Magenta
Write-Host "=========================" -ForegroundColor Magenta

$loadTestBody = @{
    text = "Test de charge pour Kubernetes"
    model = "simple"
}

$startTime = Get-Date
$requests = 10
$successfulRequests = 0

Write-Host "Envoi de $requests requêtes..."

for ($i = 1; $i -le $requests; $i++) {
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/analyze" -Method POST -Body ($loadTestBody | ConvertTo-Json) -Headers @{"Content-Type"="application/json"} -TimeoutSec 10
        $successfulRequests++
        Write-Host "." -NoNewline -ForegroundColor Green
    }
    catch {
        Write-Host "X" -NoNewline -ForegroundColor Red
    }
}

$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds
$requestsPerSecond = [math]::Round($requests / $duration, 2)

Write-Host ""
Write-Host "Requêtes réussies: $successfulRequests/$requests"
Write-Host "Durée totale: $([math]::Round($duration, 2))s"
Write-Host "Requêtes/seconde: $requestsPerSecond"

# Vérifications Kubernetes
Write-Host ""
Write-Host "🚢 ÉTAT KUBERNETES" -ForegroundColor Magenta
Write-Host "==================" -ForegroundColor Magenta

try {
    $pods = kubectl get pods -n digital-social-score -o json | ConvertFrom-Json
    $runningPods = ($pods.items | Where-Object { $_.status.phase -eq "Running" }).Count
    $totalPods = $pods.items.Count
    
    Write-Host "Pods en cours d'exécution: $runningPods/$totalPods"
    
    if ($runningPods -eq $totalPods -and $totalPods -gt 0) {
        Write-Host "✅ Tous les pods sont opérationnels" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Certains pods ne sont pas en cours d'exécution" -ForegroundColor Yellow
    }
    
    # Afficher les pods
    Write-Host "`nDétail des pods:"
    kubectl get pods -n digital-social-score
    
} catch {
    Write-Host "❌ Impossible de récupérer l'état des pods Kubernetes" -ForegroundColor Red
    Write-Host "   Vérifiez que kubectl est configuré et que le namespace existe" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 RECOMMANDATIONS" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan

if ($successRate -eq 100) {
    Write-Host "✅ API Kubernetes prête pour production"
    Write-Host "✅ Vous pouvez passer à l'Étape 4 (Sécurité)"
} else {
    Write-Host "⚠️  Corrigez les erreurs avant de continuer"
    Write-Host "📝 Vérifiez les logs: kubectl logs -f deployment/dss-api-deployment -n digital-social-score"
}

Write-Host ""
Write-Host "🔗 LIENS UTILES" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan
Write-Host "Documentation API: $BaseUrl/docs"
Write-Host "Health Check: $BaseUrl/health"
Write-Host "Monitoring: kubectl top pods -n digital-social-score"
