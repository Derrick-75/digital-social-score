# Script PowerShell de déploiement Kubernetes pour Digital Social Score API

param(
    [string]$ImageTag = "latest",
    [switch]$SkipBuild = $false
)

Write-Host "🚀 Déploiement Kubernetes - Digital Social Score API" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Variables
$NAMESPACE = "digital-social-score"
$APP_NAME = "dss-api"

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   Namespace: $NAMESPACE"
Write-Host "   App: $APP_NAME"
Write-Host "   Image Tag: $ImageTag"
Write-Host ""

# Vérifier si kubectl est installé
try {
    kubectl version --client --short | Out-Null
    Write-Host "✅ kubectl trouvé" -ForegroundColor Green
} catch {
    Write-Host "❌ kubectl n'est pas installé ou n'est pas dans le PATH" -ForegroundColor Red
    Write-Host "   Installez kubectl: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/"
    exit 1
}

# Vérifier la connexion au cluster
Write-Host "🔍 Vérification de la connexion au cluster..." -ForegroundColor Yellow
try {
    kubectl cluster-info | Out-Null
    Write-Host "✅ Connexion au cluster OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Impossible de se connecter au cluster Kubernetes" -ForegroundColor Red
    Write-Host "   Vérifiez votre configuration kubectl (kubeconfig)" -ForegroundColor Red
    exit 1
}

# Build de l'image Docker si nécessaire
if (-not $SkipBuild) {
    Write-Host "🔨 Build de l'image Docker..." -ForegroundColor Yellow
    docker build -t digital-social-score-api:$ImageTag .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erreur lors du build Docker" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Image Docker créée" -ForegroundColor Green
}

# Créer le namespace
Write-Host "📁 Création du namespace..." -ForegroundColor Yellow
kubectl apply -f k8s/namespace.yaml

# Attendre que le namespace soit créé
kubectl wait --for=condition=Active namespace/$NAMESPACE --timeout=30s

# Appliquer les ConfigMaps et Secrets
Write-Host "⚙️  Application des ConfigMaps et Secrets..." -ForegroundColor Yellow
kubectl apply -f k8s/configmap.yaml

# Déployer l'application
Write-Host "🚢 Déploiement de l'application..." -ForegroundColor Yellow
kubectl apply -f k8s/deployment.yaml

# Créer les services
Write-Host "🌐 Création des services..." -ForegroundColor Yellow
kubectl apply -f k8s/service.yaml

# Créer l'ingress
Write-Host "🌍 Configuration de l'ingress..." -ForegroundColor Yellow
kubectl apply -f k8s/ingress.yaml

# Configurer l'autoscaling
Write-Host "📈 Configuration de l'autoscaling..." -ForegroundColor Yellow
kubectl apply -f k8s/hpa.yaml

# Attendre que le déploiement soit prêt
Write-Host "⏳ Attente du déploiement..." -ForegroundColor Yellow
kubectl rollout status deployment/$APP_NAME-deployment -n $NAMESPACE --timeout=300s

# Vérifier l'état des pods
Write-Host "🔍 État des pods:" -ForegroundColor Yellow
kubectl get pods -n $NAMESPACE -l app=$APP_NAME

# Afficher les services
Write-Host "🌐 Services disponibles:" -ForegroundColor Yellow
kubectl get services -n $NAMESPACE

# Afficher l'ingress
Write-Host "🌍 Ingress configuré:" -ForegroundColor Yellow
kubectl get ingress -n $NAMESPACE

# Instructions finales
Write-Host ""
Write-Host "✅ Déploiement terminé avec succès!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Commandes utiles:" -ForegroundColor Cyan
Write-Host "   Voir les pods: kubectl get pods -n $NAMESPACE"
Write-Host "   Voir les logs: kubectl logs -f deployment/$APP_NAME-deployment -n $NAMESPACE"
Write-Host "   Exposer localement: kubectl port-forward service/$APP_NAME-service 8080:80 -n $NAMESPACE"
Write-Host "   Supprimer: kubectl delete namespace $NAMESPACE"
Write-Host ""
Write-Host "🌐 API accessible via:" -ForegroundColor Cyan
Write-Host "   Port-forward: http://localhost:8080"
Write-Host "   NodePort: http://<node-ip>:30001"
Write-Host "   Ingress: https://dss-api.votre-domaine.com (après configuration DNS)"

# Optionnel : Port-forward automatique pour test local
$response = Read-Host "Voulez-vous démarrer un port-forward pour tester localement ? (o/N)"
if ($response -eq "o" -or $response -eq "O") {
    Write-Host "🔄 Démarrage du port-forward..." -ForegroundColor Yellow
    Write-Host "   API sera accessible sur http://localhost:8080"
    Write-Host "   Appuyez sur Ctrl+C pour arrêter"
    kubectl port-forward service/$APP_NAME-service 8080:80 -n $NAMESPACE
}
