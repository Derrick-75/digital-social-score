#!/bin/bash

# Script de déploiement Kubernetes pour Digital Social Score API
echo "🚀 Déploiement Kubernetes - Digital Social Score API"
echo "=================================================="

# Variables
NAMESPACE="digital-social-score"
APP_NAME="dss-api"
IMAGE_TAG=${1:-"latest"}

echo "📋 Configuration:"
echo "   Namespace: $NAMESPACE"
echo "   App: $APP_NAME"
echo "   Image Tag: $IMAGE_TAG"
echo ""

# Vérifier si kubectl est installé
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl n'est pas installé ou n'est pas dans le PATH"
    exit 1
fi

# Vérifier la connexion au cluster
echo "🔍 Vérification de la connexion au cluster..."
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Impossible de se connecter au cluster Kubernetes"
    echo "   Vérifiez votre configuration kubectl"
    exit 1
fi

echo "✅ Connexion au cluster OK"

# Créer le namespace
echo "📁 Création du namespace..."
kubectl apply -f k8s/namespace.yaml

# Attendre que le namespace soit créé
kubectl wait --for=condition=Active namespace/$NAMESPACE --timeout=30s

# Appliquer les ConfigMaps et Secrets
echo "⚙️  Application des ConfigMaps et Secrets..."
kubectl apply -f k8s/configmap.yaml

# Déployer l'application
echo "🚢 Déploiement de l'application..."
kubectl apply -f k8s/deployment.yaml

# Créer les services
echo "🌐 Création des services..."
kubectl apply -f k8s/service.yaml

# Créer l'ingress
echo "🌍 Configuration de l'ingress..."
kubectl apply -f k8s/ingress.yaml

# Configurer l'autoscaling
echo "📈 Configuration de l'autoscaling..."
kubectl apply -f k8s/hpa.yaml

# Attendre que le déploiement soit prêt
echo "⏳ Attente du déploiement..."
kubectl rollout status deployment/$APP_NAME-deployment -n $NAMESPACE --timeout=300s

# Vérifier l'état des pods
echo "🔍 État des pods:"
kubectl get pods -n $NAMESPACE -l app=$APP_NAME

# Afficher les services
echo "🌐 Services disponibles:"
kubectl get services -n $NAMESPACE

# Afficher l'ingress
echo "🌍 Ingress configuré:"
kubectl get ingress -n $NAMESPACE

# Instructions finales
echo ""
echo "✅ Déploiement terminé avec succès!"
echo ""
echo "📝 Commandes utiles:"
echo "   Voir les pods: kubectl get pods -n $NAMESPACE"
echo "   Voir les logs: kubectl logs -f deployment/$APP_NAME-deployment -n $NAMESPACE"
echo "   Exposer localement: kubectl port-forward service/$APP_NAME-service 8080:80 -n $NAMESPACE"
echo "   Supprimer: kubectl delete namespace $NAMESPACE"
echo ""
echo "🌐 API accessible via:"
echo "   Port-forward: http://localhost:8080"
echo "   NodePort: http://<node-ip>:30001"
echo "   Ingress: https://dss-api.votre-domaine.com (après configuration DNS)"
