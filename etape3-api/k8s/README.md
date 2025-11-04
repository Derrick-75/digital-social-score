# Kubernetes Configuration pour Digital Social Score API

Ce dossier contient tous les manifests Kubernetes pour déployer l'API Digital Social Score sur différentes plateformes.

## 📁 Structure

```
k8s/
├── 📋 Manifests Kubernetes
│   ├── namespace.yaml      # Namespace isolé pour l'application
│   ├── configmap.yaml      # Configuration et secrets
│   ├── deployment.yaml     # Déploiement principal de l'API
│   ├── service.yaml        # Services (ClusterIP + NodePort)
│   ├── ingress.yaml        # Exposition externe avec HTTPS
│   └── hpa.yaml           # Auto-scaling horizontal
├── 🔧 Scripts de Déploiement
│   ├── deploy.sh          # Déploiement local (Linux/Mac)
│   ├── deploy.ps1         # Déploiement local (Windows)
│   ├── test-k8s.ps1       # Tests automatisés
│   └── gcp-setup.ps1      # Configuration GCP/GKE
├── 🌐 Déploiement Cloud (GCP)
│   ├── deploy-gcp.ps1     # Déploiement sur GKE
│   ├── monitor-gcp.ps1    # Monitoring temps réel
│   ├── cleanup-gcp.ps1    # Nettoyage ressources
│   └── test-deployment-gcp.ps1  # Tests automatisés GCP
└── 📚 Documentation
    ├── README.md          # Cette documentation
    ├── KUBERNETES-QUICK-START.md  # Guide rapide
    └── GCP-DEPLOYMENT-GUIDE.md    # Guide complet GCP
```

## 🎯 Options de Déploiement

### 🏠 Déploiement Local (Development)

Pour tester en local sur minikube, Docker Desktop, ou cluster de développement.

**Prérequis :**
- Kubernetes cluster local actif
- kubectl configuré
- Docker installé

**Déploiement rapide :**
```powershell
# Windows
.\k8s\deploy.ps1

# Linux/Mac
./k8s/deploy.sh
```

### ☁️ Déploiement Cloud Production (GCP)

Pour un déploiement production sur Google Kubernetes Engine.

**Prérequis :**
- Compte Google Cloud avec facturation activée
- gcloud CLI installé et configuré
- Projet GCP créé

**Déploiement rapide :**
```powershell
# 1. Configuration du cluster GKE
.\k8s\gcp-setup.ps1 -ProjectId "votre-project-id"

# 2. Déploiement de l'application
.\k8s\deploy-gcp.ps1 -ProjectId "votre-project-id"

# 3. Monitoring en temps réel
.\k8s\monitor-gcp.ps1
```

**📖 [Guide complet GCP](GCP-DEPLOYMENT-GUIDE.md)**

## 🚀 Déploiement Rapide Local

### Prérequis

1. **Kubernetes cluster actif** (minikube, Docker Desktop, ou cluster local)
2. **kubectl configuré** et connecté au cluster
3. **Docker installé** pour construire l'image

### Option 1 : Script PowerShell (Windows)

```powershell
# Déploiement complet avec build
.\k8s\deploy.ps1

# Déploiement sans rebuild
.\k8s\deploy.ps1 -SkipBuild

# Avec tag spécifique
.\k8s\deploy.ps1 -ImageTag "v1.2.0"
```

### Option 2 : Script Bash (Linux/Mac)

```bash
# Déploiement complet
./k8s/deploy.sh

# Avec paramètres
./k8s/deploy.sh --skip-build --image-tag v1.2.0
```

### Option 3 : Déploiement manuel

```bash
# 1. Build de l'image (si pas fait)
docker build -t digital-social-score-api:latest .

# 2. Déploiement des manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# 3. Exposition (optionnel)
kubectl apply -f k8s/ingress.yaml
```

## 🧪 Tests et Validation

### Tests automatisés locaux

```powershell
# Tests complets avec rapport
.\k8s\test-k8s.ps1 -Verbose -ExportReport

# Tests simples
.\k8s\test-k8s.ps1
```

### Tests GCP

```powershell
# Tests de déploiement GCP
.\k8s\test-deployment-gcp.ps1 -Verbose -ExportReport

# Tests avec URL spécifique
.\k8s\test-deployment-gcp.ps1 -BaseUrl "https://votre-domaine.com"
```

### Surveillance et Monitoring

```powershell
# Monitoring local
kubectl get pods -n digital-social-score -w

# Monitoring GCP avancé
.\k8s\monitor-gcp.ps1 -ShowLogs -RefreshInterval 15
```

## 🌐 Déploiement Production GCP

### Configuration initiale

```powershell
# 1. Configuration du cluster GKE
.\k8s\gcp-setup.ps1 -ProjectId "votre-project-id" -ClusterName "dss-prod" -Zone "europe-west1-b"
```

### Déploiement avec différentes options

```powershell
# Déploiement standard
.\k8s\deploy-gcp.ps1 -ProjectId "votre-project-id"

# Avec LoadBalancer externe
.\k8s\deploy-gcp.ps1 -ProjectId "votre-project-id" -UseLoadBalancer

# Avec domaine personnalisé et SSL
.\k8s\deploy-gcp.ps1 -ProjectId "votre-project-id" -Domain "api.votre-domaine.com"
```

### Monitoring et maintenance

```powershell
# Surveillance temps réel
.\k8s\monitor-gcp.ps1 -ShowLogs -ExportMetrics

# Tests de charge
.\k8s\test-deployment-gcp.ps1 -BaseUrl "https://api.votre-domaine.com"

# Nettoyage (développement)
.\k8s\cleanup-gcp.ps1 -DeleteImages

# Suppression complète
.\k8s\cleanup-gcp.ps1 -DeleteCluster -DeleteImages -Force
```

# 2. Déploiement des manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

# 3. Vérifier le déploiement
kubectl rollout status deployment/dss-api-deployment -n digital-social-score
```

## 🔧 Configuration

### Variables d'environnement

Les variables sont définies dans `configmap.yaml` :

- `APP_NAME` : Nom de l'application
- `LOG_LEVEL` : Niveau de log (info, debug, warning)
- `CORS_ORIGINS` : Origines autorisées pour CORS
- `RATE_LIMIT_REQUESTS` : Limite de requêtes par minute
- `MAX_REQUEST_SIZE` : Taille maximale des requêtes

### Secrets

Les secrets sensibles dans `configmap.yaml` (section Secret) :

- `JWT_SECRET_KEY` : Clé secrète pour JWT (base64)
- `API_KEY` : Clé API pour authentification (base64)

**⚠️ Important** : Changez les valeurs par défaut avant le déploiement !

## 🌐 Accès à l'API

### 1. Port-forward (Test local)

```powershell
kubectl port-forward service/dss-api-service 8080:80 -n digital-social-score
```

API accessible sur : `http://localhost:8080`

### 2. NodePort (Accès direct)

```powershell
kubectl get nodes -o wide  # Obtenir l'IP du node
```

API accessible sur : `http://<node-ip>:30001`

### 3. Ingress (Production avec domaine)

1. Configurer un nom de domaine pointant vers votre cluster
2. Modifier `ingress.yaml` avec votre domaine
3. Installer cert-manager pour les certificats SSL automatiques

API accessible sur : `https://dss-api.votre-domaine.com`

## 📊 Monitoring

### Vérifier l'état

```powershell
# État des pods
kubectl get pods -n digital-social-score

# Logs de l'application
kubectl logs -f deployment/dss-api-deployment -n digital-social-score

# État des services
kubectl get services -n digital-social-score

# Métriques d'autoscaling
kubectl get hpa -n digital-social-score
```

### Health Check

L'API expose un endpoint de santé sur `/health` qui est utilisé par :

- **Liveness Probe** : Redémarre le pod si l'API ne répond pas
- **Readiness Probe** : Retire le pod du load balancing s'il n'est pas prêt

## 🔄 Auto-scaling

L'HPA (Horizontal Pod Autoscaler) est configuré pour :

- **Min replicas** : 2
- **Max replicas** : 10
- **CPU threshold** : 70%
- **Memory threshold** : 80%

### Tester l'autoscaling

```powershell
# Générer de la charge
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh
# Dans le pod:
while true; do wget -q -O- http://dss-api-service.digital-social-score.svc.cluster.local/health; done
```

## 🛡️ Sécurité

### Network Policies (Optionnel)

Pour isoler le trafic réseau, créez des Network Policies :

```yaml
# Exemple: autoriser uniquement le trafic HTTP entrant
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: dss-api-netpol
  namespace: digital-social-score
spec:
  podSelector:
    matchLabels:
      app: dss-api
  policyTypes:
  - Ingress
  ingress:
  - from: []
    ports:
    - protocol: TCP
      port: 8000
```

### Secrets Management

Pour la production, utilisez des solutions comme :

- **External Secrets Operator**
- **HashiCorp Vault**
- **Azure Key Vault** / **AWS Secrets Manager** / **GCP Secret Manager**

## 🧹 Nettoyage

### Supprimer le déploiement

```powershell
# Supprimer tout le namespace (plus rapide)
kubectl delete namespace digital-social-score

# Ou supprimer individuellement
kubectl delete -f k8s/
```

## 🐛 Troubleshooting

### Problèmes courants

1. **Pods en état CrashLoopBackOff**
   ```powershell
   kubectl describe pod <pod-name> -n digital-social-score
   kubectl logs <pod-name> -n digital-social-score
   ```

2. **Image non trouvée**
   - Vérifiez que l'image Docker est construite localement
   - Ou poussez l'image sur un registry accessible

3. **Service inaccessible**
   ```powershell
   kubectl get endpoints -n digital-social-score
   kubectl describe service dss-api-service -n digital-social-score
   ```

### Commandes de diagnostic

```powershell
# Vue d'ensemble
kubectl get all -n digital-social-score

# Événements du cluster
kubectl get events -n digital-social-score --sort-by='.lastTimestamp'

# Description détaillée
kubectl describe deployment dss-api-deployment -n digital-social-score
```

## 📈 Métriques et Observabilité

### Prometheus (Optionnel)

Pour le monitoring avancé, installez Prometheus + Grafana :

```powershell
# Ajouter le repo Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Installer Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

### Métriques exposées

L'API peut exposer des métriques custom sur `/metrics` (à implémenter) :

- Nombre de requêtes par endpoint
- Temps de réponse P95/P99
- Erreurs par type
- Utilisation mémoire/CPU

---

## 🎯 Prochaines Étapes

1. **Étape 4** : Ajouter JWT et HTTPS
2. **Étape 5** : Tests de charge avec Kubernetes
3. **Étape 6** : Monitoring et alerting
4. **Cloud** : Déploiement sur AKS/EKS/GKE

**Status** : ✅ Prêt pour déploiement Kubernetes
