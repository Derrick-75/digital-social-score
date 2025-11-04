# Script de Déploiement GCP pour Digital Social Score API
# Prérequis : gcp-setup.ps1 exécuté avec succès

param(
    [string]$ProjectId = "",
    [string]$ImageTag = "latest",
    [string]$Domain = "",
    [switch]$UseLoadBalancer = $false
)

Write-Host "🚀 Déploiement Digital Social Score sur GCP" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

# Vérification des prérequis
Write-Host "`n1️⃣ Vérification des prérequis..." -ForegroundColor Yellow

# Vérifier que nous sommes connectés à GCP
try {
    $currentProject = gcloud config get-value project 2>$null
    if (-not $currentProject) {
        throw "Pas de projet configuré"
    }
    if ($ProjectId -and $currentProject -ne $ProjectId) {
        Write-Host "Configuration du projet: $ProjectId" -ForegroundColor Blue
        gcloud config set project $ProjectId
        $currentProject = $ProjectId
    }
    Write-Host "✅ Projet GCP: $currentProject" -ForegroundColor Green
} catch {
    Write-Host "❌ Non connecté à GCP. Exécutez d'abord: .\gcp-setup.ps1" -ForegroundColor Red
    exit 1
}

# Vérifier kubectl context
try {
    $context = kubectl config current-context 2>$null
    if (-not $context -or $context -notmatch "gke_") {
        throw "Pas de contexte GKE"
    }
    Write-Host "✅ Contexte Kubernetes: $context" -ForegroundColor Green
} catch {
    Write-Host "❌ kubectl non configuré pour GKE. Exécutez: .\gcp-setup.ps1" -ForegroundColor Red
    exit 1
}

# Construction et push de l'image Docker
Write-Host "`n2️⃣ Construction et upload de l'image Docker..." -ForegroundColor Yellow

$imageName = "gcr.io/$currentProject/digital-social-score"
$fullImageName = "$imageName`:$ImageTag"

Write-Host "Image: $fullImageName" -ForegroundColor Blue

# Configuration Docker pour GCR
Write-Host "Configuration Docker pour Google Container Registry..." -ForegroundColor Blue
gcloud auth configure-docker --quiet

# Build de l'image depuis le répertoire parent
$parentDir = Split-Path -Parent $PSScriptRoot
Push-Location $parentDir

try {
    Write-Host "Construction de l'image Docker..." -ForegroundColor Blue
    docker build -t $fullImageName .
    
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur lors du build Docker"
    }
    
    Write-Host "Upload vers Google Container Registry..." -ForegroundColor Blue
    docker push $fullImageName
    
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur lors du push vers GCR"
    }
    
    Write-Host "✅ Image Docker uploadée avec succès" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur lors de la construction/upload de l'image: $_" -ForegroundColor Red
    Pop-Location
    exit 1
} finally {
    Pop-Location
}

# Préparation des manifests Kubernetes
Write-Host "`n3️⃣ Préparation des manifests Kubernetes..." -ForegroundColor Yellow

# Création d'un fichier temporaire avec la bonne image
$tempDeployment = "deployment-gcp.yaml"
$deploymentContent = Get-Content "deployment.yaml" -Raw
$deploymentContent = $deploymentContent -replace "digital-social-score:latest", $fullImageName

# Ajout de ressources optimisées pour GCP
$deploymentContent = $deploymentContent -replace "replicas: 2", "replicas: 3"
$deploymentContent = $deploymentContent -replace "memory: `"512Mi`"", "memory: `"1Gi`""
$deploymentContent = $deploymentContent -replace "memory: `"1Gi`"", "memory: `"2Gi`""

Set-Content -Path $tempDeployment -Value $deploymentContent
Write-Host "✅ Manifests préparés pour GCP" -ForegroundColor Green

# Déploiement sur GKE
Write-Host "`n4️⃣ Déploiement sur Google Kubernetes Engine..." -ForegroundColor Yellow

try {
    # Création du namespace
    Write-Host "Création du namespace..." -ForegroundColor Blue
    kubectl apply -f namespace.yaml
    
    # Attendre que le namespace soit prêt
    kubectl wait --for=condition=Active namespace/digital-social-score --timeout=60s
    
    # Déploiement des ConfigMaps et Secrets
    Write-Host "Déploiement des configurations..." -ForegroundColor Blue
    kubectl apply -f configmap.yaml
    
    # Déploiement de l'application
    Write-Host "Déploiement de l'application..." -ForegroundColor Blue
    kubectl apply -f $tempDeployment
    
    # Déploiement des services
    Write-Host "Déploiement des services..." -ForegroundColor Blue
    kubectl apply -f service.yaml
    
    # Configuration de l'autoscaling
    Write-Host "Configuration de l'autoscaling..." -ForegroundColor Blue
    kubectl apply -f hpa.yaml
    
    Write-Host "✅ Application déployée avec succès" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Erreur lors du déploiement: $_" -ForegroundColor Red
    exit 1
} finally {
    # Nettoyage du fichier temporaire
    if (Test-Path $tempDeployment) {
        Remove-Item $tempDeployment
    }
}

# Configuration de l'accès externe
Write-Host "`n5️⃣ Configuration de l'accès externe..." -ForegroundColor Yellow

if ($UseLoadBalancer) {
    Write-Host "Création d'un LoadBalancer GCP..." -ForegroundColor Blue
    
    $lbService = @"
apiVersion: v1
kind: Service
metadata:
  name: dss-api-loadbalancer
  namespace: digital-social-score
  annotations:
    cloud.google.com/load-balancer-type: "External"
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  selector:
    app: digital-social-score
"@
    
    $lbService | kubectl apply -f -
    
    Write-Host "Attente de l'IP externe du LoadBalancer..." -ForegroundColor Blue
    $timeout = 300 # 5 minutes
    $elapsed = 0
    do {
        Start-Sleep 10
        $elapsed += 10
        $externalIP = kubectl get service dss-api-loadbalancer -n digital-social-score -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>$null
        if ($externalIP) {
            Write-Host "✅ LoadBalancer créé avec IP: $externalIP" -ForegroundColor Green
            break
        }
        if ($elapsed -ge $timeout) {
            Write-Host "⚠️ Timeout lors de l'attente de l'IP du LoadBalancer" -ForegroundColor Yellow
            break
        }
    } while (-not $externalIP)
} else {
    # Configuration Ingress avec certificat SSL automatique
    if ($Domain) {
        Write-Host "Configuration de l'Ingress avec domaine: $Domain" -ForegroundColor Blue
        
        # Mise à jour du fichier ingress avec le domaine
        $ingressContent = Get-Content "ingress.yaml" -Raw
        $ingressContent = $ingressContent -replace "your-domain\.com", $Domain
        
        # Ajout des annotations GCP spécifiques
        $ingressContent = $ingressContent -replace "nginx", "gce"
        $ingressContent = $ingressContent -replace "annotations:", @"
annotations:
    kubernetes.io/ingress.class: "gce"
    kubernetes.io/ingress.global-static-ip-name: "dss-api-ip"
    networking.gke.io/managed-certificates: "dss-api-ssl-cert"
"@
        
        # Création du certificat managé
        $managedCert = @"
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: dss-api-ssl-cert
  namespace: digital-social-score
spec:
  domains:
    - $Domain
"@
        
        $managedCert | kubectl apply -f -
        $ingressContent | kubectl apply -f -
        
        Write-Host "✅ Ingress configuré avec SSL automatique pour $Domain" -ForegroundColor Green
    } else {
        Write-Host "Déploiement de l'Ingress standard..." -ForegroundColor Blue
        kubectl apply -f ingress.yaml
        Write-Host "✅ Ingress déployé" -ForegroundColor Green
    }
}

# Vérification du déploiement
Write-Host "`n6️⃣ Vérification du déploiement..." -ForegroundColor Yellow

Write-Host "Attente du démarrage des pods..." -ForegroundColor Blue
kubectl wait --for=condition=ready pod -l app=digital-social-score -n digital-social-score --timeout=300s

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Pods démarrés avec succès" -ForegroundColor Green
} else {
    Write-Host "⚠️ Certains pods mettent du temps à démarrer" -ForegroundColor Yellow
}

# Affichage du statut
Write-Host "`n📊 Statut du déploiement:" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

kubectl get pods -n digital-social-score
Write-Host ""
kubectl get services -n digital-social-score
Write-Host ""
kubectl get ingress -n digital-social-score

# Instructions de test
Write-Host "`n🧪 Tests de l'API:" -ForegroundColor Yellow
Write-Host "==================" -ForegroundColor Yellow

if ($UseLoadBalancer -and $externalIP) {
    $testUrl = "http://$externalIP"
    Write-Host "LoadBalancer IP: $externalIP" -ForegroundColor Cyan
    Write-Host "Test: curl $testUrl/health" -ForegroundColor White
} elseif ($Domain) {
    $testUrl = "https://$Domain"
    Write-Host "Domaine: $Domain" -ForegroundColor Cyan
    Write-Host "Test: curl $testUrl/health" -ForegroundColor White
} else {
    Write-Host "Port-forward pour test local:" -ForegroundColor Cyan
    Write-Host "kubectl port-forward -n digital-social-score service/dss-api-service 8080:80" -ForegroundColor White
    Write-Host "Test: curl http://localhost:8080/health" -ForegroundColor White
}

# Test automatique
Write-Host "`n🔍 Test automatique de l'API..." -ForegroundColor Yellow
Start-Sleep 5

$nodePort = kubectl get service dss-api-nodeport -n digital-social-score -o jsonpath='{.spec.ports[0].nodePort}' 2>$null
if ($nodePort) {
    $nodeIP = kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}' 2>$null
    if (-not $nodeIP) {
        $nodeIP = kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}'
    }
    
    if ($nodeIP -and $nodePort) {
        try {
            $response = Invoke-RestMethod -Uri "http://$nodeIP`:$nodePort/health" -TimeoutSec 10 -ErrorAction Stop
            Write-Host "✅ API répond correctement: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
        } catch {
            Write-Host "⚠️ Test automatique échoué. Testez manuellement." -ForegroundColor Yellow
        }
    }
}

Write-Host "`n✅ Déploiement GCP terminé avec succès!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host "Projet GCP: $currentProject" -ForegroundColor Cyan
Write-Host "Image: $fullImageName" -ForegroundColor Cyan
Write-Host "Namespace: digital-social-score" -ForegroundColor Cyan

if ($Domain) {
    Write-Host "URL publique: https://$Domain" -ForegroundColor Cyan
} elseif ($UseLoadBalancer -and $externalIP) {
    Write-Host "LoadBalancer IP: $externalIP" -ForegroundColor Cyan
}

Write-Host "`n📚 Commandes utiles:" -ForegroundColor Yellow
Write-Host "kubectl get pods -n digital-social-score" -ForegroundColor White
Write-Host "kubectl logs -f deployment/digital-social-score -n digital-social-score" -ForegroundColor White
Write-Host "kubectl describe hpa -n digital-social-score" -ForegroundColor White
Write-Host "gcloud container clusters get-credentials [CLUSTER_NAME] --zone=[ZONE]" -ForegroundColor White
