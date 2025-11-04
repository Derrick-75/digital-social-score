# 🚀 Guide de Déploiement Kubernetes - Digital Social Score

## ⚡ Déploiement Express (5 minutes)

### 1. Prérequis
```powershell
# Vérifier que vous avez :
kubectl version --client
docker --version
```

### 2. Build et Deploy
```powershell
# Aller dans le dossier API
cd etape3-api

# Lancer le déploiement automatique
.\k8s\deploy.ps1
```

### 3. Test
```powershell
# Tester l'API
.\k8s\test-k8s.ps1
```

## 🎯 Résultat Attendu

Après déploiement, vous devriez avoir :

- ✅ **2 pods** actifs dans le namespace `digital-social-score`
- ✅ **API accessible** sur http://localhost:8080 (port-forward)
- ✅ **Autoscaling** configuré (2-10 replicas)
- ✅ **Health checks** fonctionnels
- ✅ **Tests API** 100% réussis

## 🔧 Dépannage Rapide

### Pods qui ne démarrent pas
```powershell
kubectl get pods -n digital-social-score
kubectl describe pod <pod-name> -n digital-social-score
kubectl logs <pod-name> -n digital-social-score
```

### Service inaccessible
```powershell
# Vérifier les services
kubectl get svc -n digital-social-score

# Port-forward manuel
kubectl port-forward service/dss-api-service 8080:80 -n digital-social-score
```

### Image non trouvée
```powershell
# Rebuild l'image
docker build -t digital-social-score-api:latest .

# Ou utiliser un registry
docker tag digital-social-score-api:latest your-registry/dss-api:latest
docker push your-registry/dss-api:latest
```

## 📋 Commandes Utiles

```powershell
# Voir tout
kubectl get all -n digital-social-score

# Logs en temps réel
kubectl logs -f deployment/dss-api-deployment -n digital-social-score

# Supprimer tout
kubectl delete namespace digital-social-score

# Redémarrer le déploiement
kubectl rollout restart deployment/dss-api-deployment -n digital-social-score
```

## 🌐 Options de Déploiement Cloud

### Option 1 : Minikube (Local)
```powershell
minikube start
kubectl config use-context minikube
# Puis déployer normalement
```

### Option 2 : Docker Desktop
- Activer Kubernetes dans Docker Desktop
- Le cluster local sera automatiquement configuré

### Option 3 : Cloud Providers

#### Azure AKS
```powershell
az aks get-credentials --resource-group myResourceGroup --name myAKSCluster
```

#### AWS EKS
```powershell
aws eks update-kubeconfig --region region-code --name my-cluster
```

#### Google GKE
```powershell
gcloud container clusters get-credentials my-cluster --zone=us-central1-a
```

## 🎯 Validation du Déploiement

Pour valider que votre déploiement Kubernetes fonctionne :

1. **Pods opérationnels** : `kubectl get pods -n digital-social-score`
2. **API accessible** : Test avec `.\k8s\test-k8s.ps1`
3. **Autoscaling configuré** : `kubectl get hpa -n digital-social-score`
4. **Services exposés** : `kubectl get svc -n digital-social-score`

## ✅ Prêt pour l'Étape 4

Une fois Kubernetes déployé avec succès, vous pouvez passer à l'Étape 4 (Sécurité) avec :
- JWT Authentication sur Kubernetes
- Ingress avec HTTPS/TLS
- Network Policies
- Secrets management
