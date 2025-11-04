# Script de Test Automatisé pour Digital Social Score sur GCP
# Validation complète du déploiement GKE

param(
    [string]$BaseUrl = "",
    [int]$TimeoutSeconds = 300,
    [switch]$Verbose = $false,
    [switch]$ExportReport = $false
)

Write-Host "🧪 Tests Automatisés - Digital Social Score GCP" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Variables globales pour le rapport
$global:TestResults = @()
$global:StartTime = Get-Date

# Fonction pour ajouter un résultat de test
function Add-TestResult {
    param(
        [string]$TestName,
        [bool]$Success,
        [string]$Details = "",
        [int]$Duration = 0
    )
    
    $result = @{
        TestName = $TestName
        Success = $Success
        Details = $Details
        Duration = $Duration
        Timestamp = Get-Date
    }
    
    $global:TestResults += $result
    
    $status = if ($Success) { "✅ PASS" } else { "❌ FAIL" }
    $durationText = if ($Duration -gt 0) { " ($Duration ms)" } else { "" }
    
    Write-Host "$status - $TestName$durationText" -ForegroundColor $(if ($Success) { "Green" } else { "Red" })
    if ($Details -and ($Verbose -or -not $Success)) {
        Write-Host "   └─ $Details" -ForegroundColor Gray
    }
}

# Fonction pour tester la connectivité kubectl
function Test-KubernetesConnectivity {
    Write-Host "`n1️⃣ Tests de Connectivité Kubernetes" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan
    
    try {
        $startTime = Get-Date
        $context = kubectl config current-context 2>$null
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        
        if ($context -and $context -match "gke_") {
            Add-TestResult "Contexte kubectl GKE" $true "Contexte: $context" $duration
        } else {
            Add-TestResult "Contexte kubectl GKE" $false "Contexte invalide: $context"
            return $false
        }
    } catch {
        Add-TestResult "Contexte kubectl GKE" $false "Erreur: $_"
        return $false
    }
    
    try {
        $startTime = Get-Date
        $nodes = kubectl get nodes --no-headers 2>$null | Measure-Object
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        
        if ($nodes.Count -gt 0) {
            Add-TestResult "Nœuds GKE disponibles" $true "$($nodes.Count) nœud(s) trouvé(s)" $duration
        } else {
            Add-TestResult "Nœuds GKE disponibles" $false "Aucun nœud trouvé"
            return $false
        }
    } catch {
        Add-TestResult "Nœuds GKE disponibles" $false "Erreur: $_"
        return $false
    }
    
    try {
        $startTime = Get-Date
        $namespace = kubectl get namespace digital-social-score 2>$null
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        
        if ($LASTEXITCODE -eq 0) {
            Add-TestResult "Namespace digital-social-score" $true "Namespace actif" $duration
        } else {
            Add-TestResult "Namespace digital-social-score" $false "Namespace non trouvé"
            return $false
        }
    } catch {
        Add-TestResult "Namespace digital-social-score" $false "Erreur: $_"
        return $false
    }
    
    return $true
}

# Fonction pour tester les ressources Kubernetes
function Test-KubernetesResources {
    Write-Host "`n2️⃣ Tests des Ressources Kubernetes" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan
    
    # Test des deployments
    try {
        $startTime = Get-Date
        $deployments = kubectl get deployments -n digital-social-score --no-headers 2>$null
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        
        if ($deployments) {
            $deploymentCount = ($deployments | Measure-Object).Count
            Add-TestResult "Deployments créés" $true "$deploymentCount deployment(s)" $duration
        } else {
            Add-TestResult "Deployments créés" $false "Aucun deployment trouvé"
        }
    } catch {
        Add-TestResult "Deployments créés" $false "Erreur: $_"
    }
    
    # Test des pods
    try {
        $startTime = Get-Date
        $pods = kubectl get pods -n digital-social-score --no-headers 2>$null
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        
        if ($pods) {
            $podCount = ($pods | Measure-Object).Count
            $runningPods = ($pods | Where-Object { $_ -match "Running" } | Measure-Object).Count
            
            if ($runningPods -gt 0) {
                Add-TestResult "Pods en cours d'exécution" $true "$runningPods/$podCount pod(s) Running" $duration
            } else {
                Add-TestResult "Pods en cours d'exécution" $false "Aucun pod Running ($podCount total)"
            }
        } else {
            Add-TestResult "Pods en cours d'exécution" $false "Aucun pod trouvé"
        }
    } catch {
        Add-TestResult "Pods en cours d'exécution" $false "Erreur: $_"
    }
    
    # Test des services
    try {
        $startTime = Get-Date
        $services = kubectl get services -n digital-social-score --no-headers 2>$null
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        
        if ($services) {
            $serviceCount = ($services | Measure-Object).Count
            Add-TestResult "Services créés" $true "$serviceCount service(s)" $duration
        } else {
            Add-TestResult "Services créés" $false "Aucun service trouvé"
        }
    } catch {
        Add-TestResult "Services créés" $false "Erreur: $_"
    }
    
    # Test HPA (Horizontal Pod Autoscaler)
    try {
        $startTime = Get-Date
        $hpa = kubectl get hpa -n digital-social-score --no-headers 2>$null
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        
        if ($hpa) {
            Add-TestResult "HPA configuré" $true "Autoscaling actif" $duration
        } else {
            Add-TestResult "HPA configuré" $false "HPA non trouvé"
        }
    } catch {
        Add-TestResult "HPA configuré" $false "Erreur: $_"
    }
}

# Fonction pour tester les endpoints de l'API
function Test-APIEndpoints {
    param([string]$BaseUrl)
    
    Write-Host "`n3️⃣ Tests des Endpoints API" -ForegroundColor Cyan
    Write-Host "============================" -ForegroundColor Cyan
    
    if (-not $BaseUrl) {
        # Tentative de récupération de l'URL via LoadBalancer
        $lbIP = kubectl get service dss-api-loadbalancer -n digital-social-score -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>$null
        if ($lbIP) {
            $BaseUrl = "http://$lbIP"
        } else {
            # Fallback sur NodePort
            $nodePort = kubectl get service dss-api-nodeport -n digital-social-score -o jsonpath='{.spec.ports[0].nodePort}' 2>$null
            $nodeIP = kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}' 2>$null
            
            if (-not $nodeIP) {
                $nodeIP = kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}'
            }
            
            if ($nodeIP -and $nodePort) {
                $BaseUrl = "http://$nodeIP`:$nodePort"
            } else {
                Add-TestResult "Détection URL API" $false "Impossible de déterminer l'URL de l'API"
                Write-Host "⚠️ Utilisez port-forward pour tester localement:" -ForegroundColor Yellow
                Write-Host "kubectl port-forward -n digital-social-score service/dss-api-service 8080:80" -ForegroundColor White
                return
            }
        }
    }
    
    Add-TestResult "Détection URL API" $true "URL: $BaseUrl"
    
    # Test de l'endpoint /health
    try {
        $startTime = Get-Date
        $response = Invoke-RestMethod -Uri "$BaseUrl/health" -TimeoutSec 10 -ErrorAction Stop
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        
        if ($response) {
            Add-TestResult "Endpoint /health" $true "Réponse reçue" $duration
        } else {
            Add-TestResult "Endpoint /health" $false "Réponse vide"
        }
    } catch {
        Add-TestResult "Endpoint /health" $false "Erreur: $($_.Exception.Message)"
    }
    
    # Test de l'endpoint /docs (Swagger)
    try {
        $startTime = Get-Date
        $response = Invoke-WebRequest -Uri "$BaseUrl/docs" -TimeoutSec 10 -ErrorAction Stop
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        
        if ($response.StatusCode -eq 200) {
            Add-TestResult "Endpoint /docs" $true "Documentation accessible" $duration
        } else {
            Add-TestResult "Endpoint /docs" $false "Status: $($response.StatusCode)"
        }
    } catch {
        Add-TestResult "Endpoint /docs" $false "Erreur: $($_.Exception.Message)"
    }
    
    # Test de l'endpoint /predict
    try {
        $startTime = Get-Date
        $testPayload = @{
            text = "Ceci est un test de prédiction de toxicité"
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$BaseUrl/predict" -Method POST -Body $testPayload -ContentType "application/json" -TimeoutSec 15 -ErrorAction Stop
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        
        if ($response -and $response.prediction -ne $null) {
            $toxicity = if ($response.prediction -gt 0.5) { "Toxique" } else { "Non-toxique" }
            Add-TestResult "Endpoint /predict" $true "Prédiction: $toxicity (score: $($response.prediction))" $duration
        } else {
            Add-TestResult "Endpoint /predict" $false "Réponse invalide"
        }
    } catch {
        Add-TestResult "Endpoint /predict" $false "Erreur: $($_.Exception.Message)"
    }
}

# Fonction pour tester les performances
function Test-Performance {
    param([string]$BaseUrl)
    
    Write-Host "`n4️⃣ Tests de Performance" -ForegroundColor Cyan
    Write-Host "========================" -ForegroundColor Cyan
    
    if (-not $BaseUrl) {
        Add-TestResult "Tests de performance" $false "URL non disponible"
        return
    }
    
    # Test de charge basique (10 requêtes)
    $requests = 10
    $successful = 0
    $totalTime = 0
    
    Write-Host "Exécution de $requests requêtes de test..." -ForegroundColor Blue
    
    for ($i = 1; $i -le $requests; $i++) {
        try {
            $startTime = Get-Date
            $testPayload = @{
                text = "Test de performance $i - évaluation de toxicité"
            } | ConvertTo-Json
            
            $response = Invoke-RestMethod -Uri "$BaseUrl/predict" -Method POST -Body $testPayload -ContentType "application/json" -TimeoutSec 10 -ErrorAction Stop
            $duration = ((Get-Date) - $startTime).TotalMilliseconds
            
            if ($response.prediction -ne $null) {
                $successful++
                $totalTime += $duration
            }
            
            if ($Verbose) {
                Write-Host "  Requête $i : ${duration}ms" -ForegroundColor Gray
            }
        } catch {
            if ($Verbose) {
                Write-Host "  Requête $i : Erreur" -ForegroundColor Red
            }
        }
    }
    
    if ($successful -gt 0) {
        $averageTime = [math]::Round($totalTime / $successful, 2)
        $successRate = [math]::Round(($successful / $requests) * 100, 2)
        
        if ($successRate -ge 90 -and $averageTime -le 2000) {
            Add-TestResult "Test de charge" $true "$successRate% succès, moyenne ${averageTime}ms"
        } else {
            Add-TestResult "Test de charge" $false "$successRate% succès, moyenne ${averageTime}ms (seuils: 90%, 2000ms)"
        }
    } else {
        Add-TestResult "Test de charge" $false "Aucune requête réussie"
    }
}

# Fonction pour tester l'autoscaling
function Test-Autoscaling {
    Write-Host "`n5️⃣ Tests d'Autoscaling" -ForegroundColor Cyan
    Write-Host "=======================" -ForegroundColor Cyan
    
    try {
        $startTime = Get-Date
        $hpaStatus = kubectl get hpa -n digital-social-score -o jsonpath='{.items[0].status}' 2>$null | ConvertFrom-Json
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        
        if ($hpaStatus) {
            $currentReplicas = $hpaStatus.currentReplicas
            $desiredReplicas = $hpaStatus.desiredReplicas
            $maxReplicas = $hpaStatus.maxReplicas
            
            Add-TestResult "HPA Status" $true "Répliques: $currentReplicas/$desiredReplicas (max: $maxReplicas)" $duration
            
            # Vérification que l'HPA fonctionne
            if ($currentReplicas -ge 1 -and $currentReplicas -le $maxReplicas) {
                Add-TestResult "HPA Fonctionnel" $true "Autoscaling dans les limites"
            } else {
                Add-TestResult "HPA Fonctionnel" $false "Répliques hors limites"
            }
        } else {
            Add-TestResult "HPA Status" $false "Status HPA non disponible"
        }
    } catch {
        Add-TestResult "HPA Status" $false "Erreur: $_"
    }
    
    # Test des métriques (CPU/Memory)
    try {
        $startTime = Get-Date
        $podMetrics = kubectl top pods -n digital-social-score --no-headers 2>$null
        $duration = ((Get-Date) - $startTime).TotalMilliseconds
        
        if ($podMetrics) {
            Add-TestResult "Métriques pods" $true "Métriques disponibles" $duration
        } else {
            Add-TestResult "Métriques pods" $false "Metrics server non disponible"
        }
    } catch {
        Add-TestResult "Métriques pods" $false "Erreur: $_"
    }
}

# Fonction pour générer le rapport
function Generate-Report {
    $endTime = Get-Date
    $totalDuration = ($endTime - $global:StartTime).TotalSeconds
    
    Write-Host "`n📊 Rapport de Test" -ForegroundColor Cyan
    Write-Host "=================" -ForegroundColor Cyan
    
    $totalTests = $global:TestResults.Count
    $successfulTests = ($global:TestResults | Where-Object { $_.Success }).Count
    $failedTests = $totalTests - $successfulTests
    $successRate = if ($totalTests -gt 0) { [math]::Round(($successfulTests / $totalTests) * 100, 2) } else { 0 }
    
    Write-Host "Tests exécutés : $totalTests" -ForegroundColor White
    Write-Host "Succès         : $successfulTests" -ForegroundColor Green
    Write-Host "Échecs         : $failedTests" -ForegroundColor Red
    Write-Host "Taux de succès : $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } else { "Red" })
    Write-Host "Durée totale   : $([math]::Round($totalDuration, 2))s" -ForegroundColor White
    
    if ($ExportReport) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $reportFile = "test-report-gcp_$timestamp.json"
        
        $report = @{
            summary = @{
                totalTests = $totalTests
                successfulTests = $successfulTests
                failedTests = $failedTests
                successRate = $successRate
                duration = $totalDuration
                timestamp = $endTime
            }
            tests = $global:TestResults
        }
        
        $report | ConvertTo-Json -Depth 5 | Out-File $reportFile -Encoding UTF8
        Write-Host "`n💾 Rapport exporté : $reportFile" -ForegroundColor Blue
    }
    
    # Recommandations
    Write-Host "`n💡 Recommandations :" -ForegroundColor Yellow
    
    if ($failedTests -eq 0) {
        Write-Host "✅ Déploiement parfait ! Tous les tests passent." -ForegroundColor Green
    } elseif ($successRate -ge 80) {
        Write-Host "⚠️ Déploiement fonctionnel avec quelques problèmes mineurs." -ForegroundColor Yellow
    } else {
        Write-Host "❌ Problèmes critiques détectés. Vérifiez les logs :" -ForegroundColor Red
        Write-Host "kubectl logs -n digital-social-score --selector=app=digital-social-score" -ForegroundColor White
    }
    
    return ($successRate -ge 80)
}

# Exécution principale
Write-Host "Démarrage des tests automatisés..." -ForegroundColor Blue
Write-Host "Timeout configuré : $TimeoutSeconds secondes" -ForegroundColor Gray

# Détermination de l'URL de base si non fournie
if (-not $BaseUrl) {
    Write-Host "Détection automatique de l'URL..." -ForegroundColor Gray
}

# Exécution des tests
$kubernetesOK = Test-KubernetesConnectivity
if ($kubernetesOK) {
    Test-KubernetesResources
    Test-APIEndpoints -BaseUrl $BaseUrl
    Test-Performance -BaseUrl $BaseUrl
    Test-Autoscaling
}

# Génération du rapport final
$success = Generate-Report

if ($success) {
    Write-Host "`n🎉 Tests terminés avec succès !" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠️ Tests terminés avec des problèmes." -ForegroundColor Yellow
    exit 1
}
