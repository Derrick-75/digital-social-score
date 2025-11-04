# Script de Monitoring GCP pour Digital Social Score API
# Surveillance en temps réel du déploiement GKE

param(
    [int]$RefreshInterval = 30,
    [switch]$ShowLogs = $false,
    [switch]$ExportMetrics = $false
)

Write-Host "📊 Monitoring Digital Social Score sur GCP" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green

# Fonction pour afficher l'état du cluster
function Show-ClusterStatus {
    Write-Host "`n🔧 État du Cluster GKE:" -ForegroundColor Cyan
    Write-Host "========================" -ForegroundColor Cyan
    
    # Informations générales du cluster
    $context = kubectl config current-context 2>$null
    if ($context) {
        Write-Host "Contexte: $context" -ForegroundColor Yellow
    }
    
    # État des nœuds
    Write-Host "`n🖥️ Nœuds du cluster:" -ForegroundColor Yellow
    kubectl get nodes -o wide
    
    # Utilisation des ressources par nœud
    Write-Host "`n📈 Utilisation des ressources:" -ForegroundColor Yellow
    kubectl top nodes 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ Metrics server non disponible" -ForegroundColor Yellow
    }
}

# Fonction pour afficher l'état de l'application
function Show-ApplicationStatus {
    Write-Host "`n🚀 État de l'Application:" -ForegroundColor Cyan
    Write-Host "==========================" -ForegroundColor Cyan
    
    # Pods
    Write-Host "`n📦 Pods:" -ForegroundColor Yellow
    kubectl get pods -n digital-social-score -o wide
    
    # Services
    Write-Host "`n🌐 Services:" -ForegroundColor Yellow
    kubectl get services -n digital-social-score
    
    # Ingress
    Write-Host "`n🔗 Ingress:" -ForegroundColor Yellow
    kubectl get ingress -n digital-social-score
    
    # HPA (Horizontal Pod Autoscaler)
    Write-Host "`n📊 Autoscaling:" -ForegroundColor Yellow
    kubectl get hpa -n digital-social-score
    
    # Utilisation des ressources par pod
    Write-Host "`n💾 Utilisation des ressources par pod:" -ForegroundColor Yellow
    kubectl top pods -n digital-social-score 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ Metrics server non disponible" -ForegroundColor Yellow
    }
}

# Fonction pour tester l'API
function Test-API {
    Write-Host "`n🧪 Test de l'API:" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan
    
    # Récupération de l'IP du service
    $nodePort = kubectl get service dss-api-nodeport -n digital-social-score -o jsonpath='{.spec.ports[0].nodePort}' 2>$null
    $nodeIP = kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}' 2>$null
    
    if (-not $nodeIP) {
        $nodeIP = kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}'
    }
    
    # Test du LoadBalancer si disponible
    $lbIP = kubectl get service dss-api-loadbalancer -n digital-social-score -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>$null
    
    if ($lbIP) {
        Write-Host "🌐 Test via LoadBalancer ($lbIP):" -ForegroundColor Yellow
        try {
            $response = Invoke-RestMethod -Uri "http://$lbIP/health" -TimeoutSec 10 -ErrorAction Stop
            Write-Host "✅ Health check: OK" -ForegroundColor Green
            Write-Host "Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor White
            
            # Test de prédiction
            $testPayload = @{
                text = "Test de toxicité"
            } | ConvertTo-Json
            
            $predResponse = Invoke-RestMethod -Uri "http://$lbIP/predict" -Method POST -Body $testPayload -ContentType "application/json" -TimeoutSec 10 -ErrorAction Stop
            Write-Host "✅ Predict endpoint: OK" -ForegroundColor Green
            Write-Host "Prediction: $($predResponse | ConvertTo-Json -Compress)" -ForegroundColor White
            
        } catch {
            Write-Host "❌ LoadBalancer non accessible: $_" -ForegroundColor Red
        }
    } elseif ($nodeIP -and $nodePort) {
        Write-Host "🖥️ Test via NodePort ($nodeIP`:$nodePort):" -ForegroundColor Yellow
        try {
            $response = Invoke-RestMethod -Uri "http://$nodeIP`:$nodePort/health" -TimeoutSec 10 -ErrorAction Stop
            Write-Host "✅ Health check: OK" -ForegroundColor Green
            Write-Host "Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor White
        } catch {
            Write-Host "❌ NodePort non accessible: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️ Aucun service externe accessible. Utilisez port-forward:" -ForegroundColor Yellow
        Write-Host "kubectl port-forward -n digital-social-score service/dss-api-service 8080:80" -ForegroundColor White
    }
}

# Fonction pour afficher les logs
function Show-Logs {
    if ($ShowLogs) {
        Write-Host "`n📝 Logs récents:" -ForegroundColor Cyan
        Write-Host "=================" -ForegroundColor Cyan
        
        $pods = kubectl get pods -n digital-social-score -o jsonpath='{.items[*].metadata.name}' 2>$null
        if ($pods) {
            $podArray = $pods -split ' '
            foreach ($pod in $podArray) {
                if ($pod) {
                    Write-Host "`n📦 Logs du pod $pod`:" -ForegroundColor Yellow
                    kubectl logs $pod -n digital-social-score --tail=10 2>$null
                }
            }
        }
    }
}

# Fonction pour exporter les métriques
function Export-Metrics {
    if ($ExportMetrics) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $metricsFile = "metrics_$timestamp.json"
        
        Write-Host "`n💾 Export des métriques vers $metricsFile..." -ForegroundColor Cyan
        
        $metrics = @{
            timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
            cluster = kubectl config current-context
            nodes = kubectl get nodes -o json | ConvertFrom-Json
            pods = kubectl get pods -n digital-social-score -o json | ConvertFrom-Json
            services = kubectl get services -n digital-social-score -o json | ConvertFrom-Json
            hpa = kubectl get hpa -n digital-social-score -o json | ConvertFrom-Json
        }
        
        $metrics | ConvertTo-Json -Depth 10 | Out-File $metricsFile -Encoding UTF8
        Write-Host "✅ Métriques exportées dans $metricsFile" -ForegroundColor Green
    }
}

# Fonction principale de monitoring
function Start-Monitoring {
    Write-Host "🔄 Démarrage du monitoring (Ctrl+C pour arrêter)" -ForegroundColor Yellow
    Write-Host "Intervalle de rafraîchissement: $RefreshInterval secondes" -ForegroundColor Yellow
    
    try {
        while ($true) {
            Clear-Host
            Write-Host "📊 Monitoring Digital Social Score sur GCP - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green
            Write-Host "============================================================" -ForegroundColor Green
            
            Show-ClusterStatus
            Show-ApplicationStatus
            Test-API
            Show-Logs
            Export-Metrics
            
            Write-Host "`n⏱️ Prochaine actualisation dans $RefreshInterval secondes..." -ForegroundColor Gray
            Write-Host "Appuyez sur Ctrl+C pour arrêter" -ForegroundColor Gray
            
            Start-Sleep $RefreshInterval
        }
    } catch {
        Write-Host "`n🛑 Monitoring interrompu" -ForegroundColor Yellow
    }
}

# Fonction pour afficher l'aide
function Show-Help {
    Write-Host "`n📚 Aide du script de monitoring:" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host "Usage: .\monitor-gcp.ps1 [OPTIONS]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -RefreshInterval [secondes]  Intervalle de rafraîchissement (défaut: 30)" -ForegroundColor White
    Write-Host "  -ShowLogs                   Affiche les logs des pods" -ForegroundColor White
    Write-Host "  -ExportMetrics              Exporte les métriques en JSON" -ForegroundColor White
    Write-Host ""
    Write-Host "Exemples:" -ForegroundColor Yellow
    Write-Host "  .\monitor-gcp.ps1                        # Monitoring basique" -ForegroundColor White
    Write-Host "  .\monitor-gcp.ps1 -RefreshInterval 10    # Actualisation toutes les 10s" -ForegroundColor White
    Write-Host "  .\monitor-gcp.ps1 -ShowLogs -ExportMetrics # Monitoring complet" -ForegroundColor White
    Write-Host ""
    Write-Host "Commandes utiles:" -ForegroundColor Yellow
    Write-Host "  kubectl get pods -n digital-social-score -w  # Watch pods en temps réel" -ForegroundColor White
    Write-Host "  kubectl logs -f deployment/digital-social-score -n digital-social-score" -ForegroundColor White
    Write-Host "  kubectl describe hpa -n digital-social-score  # Détails autoscaling" -ForegroundColor White
}

# Vérification des prérequis
$context = kubectl config current-context 2>$null
if (-not $context -or $context -notmatch "gke_") {
    Write-Host "❌ kubectl non configuré pour GKE" -ForegroundColor Red
    Write-Host "Exécutez d'abord: .\gcp-setup.ps1" -ForegroundColor Yellow
    exit 1
}

# Vérification que le namespace existe
$namespace = kubectl get namespace digital-social-score 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Namespace 'digital-social-score' non trouvé" -ForegroundColor Red
    Write-Host "Exécutez d'abord: .\deploy-gcp.ps1" -ForegroundColor Yellow
    exit 1
}

# Démarrage du monitoring
Show-Help
Start-Monitoring
