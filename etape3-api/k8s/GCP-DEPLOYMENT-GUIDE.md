# Guide de Déploiement GCP - Digital Social Score API

## 🚀 Déploiement Production sur Google Cloud Platform

Ce guide vous accompagne dans le déploiement complet de l'API Digital Social Score sur Google Kubernetes Engine (GKE).

### 📋 Prérequis

#### 1. Outils requis
- **Google Cloud SDK** (gcloud CLI) - [Installation](https://cloud.google.com/sdk/docs/install)
- **Docker Desktop** - [Installation](https://docs.docker.com/desktop/)
- **kubectl** (installé automatiquement avec gcloud)
- **PowerShell 5.1+** ou **PowerShell Core 7+**

#### 2. Compte GCP
- Compte Google Cloud actif
- Projet GCP créé avec facturation activée
- Autorisations : Owner ou Editor sur le projet

#### 3. Configuration locale
```powershell
# Vérification des outils
gcloud --version
docker --version
kubectl version --client
```

### 🏗️ Architecture de Déploiement

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Cloud Build   │  │Container Registry│  │   Cloud IAM  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                Google Kubernetes Engine (GKE)               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │ │
│  │  │    Node 1    │  │    Node 2    │  │    Node 3    │  │ │
│  │  │              │  │              │  │              │  │ │
│  │  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │  │ │
│  │  │ │DSS Pod 1 │ │  │ │DSS Pod 2 │ │  │ │DSS Pod 3 │ │  │ │
│  │  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │  │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Load Balancer  │  │   Cloud DNS     │  │   SSL Cert   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 🎯 Étapes de Déploiement

#### Étape 1 : Configuration Initiale GCP

```powershell
# 1. Connexion à GCP
gcloud auth login

# 2. Configuration du projet
gcloud config set project digitalsocialscoreapiOJECT_ID

# 3. Activation de la facturation (vérifiez dans la console)
```

#### Étape 2 : Création du Cluster GKE

```powershell
# Exécution du script de configuration
.\gcp-setup.ps1 -ProjectId "digitalsocialscoreapi" -ClusterName "dss-cluster" -Zone "europe-west1-b"
```

**Ce script va :**
- ✅ Vérifier les outils installés
- ✅ Activer les APIs nécessaires (Container, Registry, Build)
- ✅ Créer un cluster GKE avec auto-scaling
- ✅ Configurer kubectl pour le cluster

**Temps estimé :** 8-12 minutes

#### Étape 3 : Déploiement de l'Application

```powershell
# Déploiement standard
.\deploy-gcp.ps1 -ProjectId "digitalsocialscoreapi"

# Déploiement avec LoadBalancer
.\deploy-gcp.ps1 -ProjectId "digitalsocialscoreapi" -UseLoadBalancer

# Déploiement avec domaine personnalisé
.\deploy-gcp.ps1 -ProjectId "digitalsocialscoreapi" -Domain "api.votre-domaine.com"
```

**Ce script va :**
- 🐳 Construire l'image Docker
- 📤 Uploader vers Google Container Registry
- 🚀 Déployer sur GKE avec auto-scaling
- 🌐 Configurer les services et ingress
- 🔒 Configurer SSL automatique (si domaine fourni)

**Temps estimé :** 5-8 minutes

#### Étape 4 : Vérification et Tests

```powershell
# Monitoring en temps réel
.\monitor-gcp.ps1 -ShowLogs -ExportMetrics

# Test manuel via port-forward
kubectl port-forward -n digital-social-score service/dss-api-service 8080:80

# Test de l'API
curl http://localhost:8080/health
curl -X POST http://localhost:8080/predict -H "Content-Type: application/json" -d '{"text":"Test de toxicité"}'
```

### 📊 Configuration des Ressources

#### Cluster GKE
- **Type de machines :** e2-medium (2 vCPU, 4 GB RAM)
- **Nœuds :** 2-5 (auto-scaling activé)
- **Région :** europe-west1-b
- **Réseaux :** VPC par défaut

#### Application
- **Répliques :** 2-10 (HPA configuré)
- **Ressources par pod :**
  - CPU : 250m-500m
  - Mémoire : 512Mi-1Gi
- **Health checks :** Liveness + Readiness probes

#### Services
- **ClusterIP :** Communication interne
- **NodePort :** Accès direct aux nœuds
- **LoadBalancer :** Accès externe via IP publique
- **Ingress :** HTTPS avec certificat SSL managé

### 🔒 Sécurité et Bonnes Pratiques

#### 1. Isolation des Ressources
```yaml
# Namespace dédié
namespace: digital-social-score

# Network Policies (optionnel)
kind: NetworkPolicy
```

#### 2. Secrets et Configuration
```yaml
# Variables d'environnement sensibles
apiVersion: v1
kind: Secret
metadata:
  name: dss-secrets
type: Opaque
```

#### 3. RBAC (Role-Based Access Control)
```yaml
# Permissions minimales par défaut
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
```

### 💰 Estimation des Coûts

#### Coûts mensuels estimés (Europe West 1) :

| Ressource | Configuration | Coût mensuel |
|-----------|---------------|--------------|
| **GKE Cluster** | 2-3 nœuds e2-medium | €60-90 |
| **Stockage persistant** | 20GB SSD | €2-3 |
| **Load Balancer** | 1 IP externe | €15-20 |
| **Trafic sortant** | <10GB/mois | €1-2 |
| **Container Registry** | <5GB images | €0.50 |
| **Cloud Build** | <100 builds/mois | Gratuit |
| **SSL Certificats** | Managés Google | Gratuit |

**Total estimé : €78-115/mois**

#### Optimisations possibles :
- 🔥 **Mode Preemptible** : -60% sur les coûts compute
- 📉 **Auto-scaling agressif** : Réduction lors des pics faibles
- 🗜️ **Images optimisées** : Réduction des coûts de stockage

### 📈 Monitoring et Observabilité

#### 1. Métriques intégrées
```powershell
# Monitoring en temps réel
.\monitor-gcp.ps1 -RefreshInterval 30 -ShowLogs

# Métriques Kubernetes natives
kubectl top nodes
kubectl top pods -n digital-social-score
```

#### 2. Google Cloud Monitoring (optionnel)
- **Dashboards** : Métriques cluster et application
- **Alertes** : CPU, mémoire, disponibilité
- **Logs** : Centralisation via Cloud Logging

#### 3. Métriques applicatives
- **Health checks** : `/health` endpoint
- **Métriques personnalisées** : Nombre de prédictions, latence

### 🔧 Maintenance et Mise à Jour

#### Mise à jour de l'application
```powershell
# Nouvelle version avec tag
.\deploy-gcp.ps1 -ImageTag "v2.0" -ProjectId "digitalsocialscoreapi"

# Rollback si nécessaire
kubectl rollout undo deployment/digital-social-score -n digital-social-score
```

#### Mise à jour du cluster
```powershell
# Mise à jour automatique activée par défaut
gcloud container clusters upgrade dss-cluster --zone=europe-west1-b
```

#### Sauvegarde et récupération
```powershell
# Export de la configuration
kubectl get all -n digital-social-score -o yaml > backup-config.yaml

# Restauration
kubectl apply -f backup-config.yaml
```

### 🧹 Nettoyage et Suppression

#### Suppression sélective
```powershell
# Suppression de l'application uniquement
kubectl delete namespace digital-social-score

# Suppression avec nettoyage complet
.\cleanup-gcp.ps1 -DeleteImages
```

#### Suppression complète
```powershell
# Suppression de tout (cluster inclus)
.\cleanup-gcp.ps1 -DeleteCluster -DeleteImages -Force
```

### ❗ Résolution de Problèmes

#### Problèmes courants

1. **Quotas dépassés**
   ```bash
   # Vérification des quotas
   gcloud compute project-info describe --project=digitalsocialscoreapi
   ```

2. **Pods en erreur**
   ```bash
   # Logs détaillés
   kubectl describe pod POD_NAME -n digital-social-score
   kubectl logs POD_NAME -n digital-social-score --previous
   ```

3. **LoadBalancer sans IP**
   ```bash
   # Vérification des quotas d'IP externes
   gcloud compute addresses list
   ```

4. **Certificat SSL en échec**
   ```bash
   # Statut du certificat managé
   kubectl describe managedcertificate -n digital-social-score
   ```

#### Support et Documentation
- 📚 [Documentation GKE](https://cloud.google.com/kubernetes-engine/docs)
- 💬 [Support Google Cloud](https://cloud.google.com/support)
- 🔧 [Kubernetes Troubleshooting](https://kubernetes.io/docs/tasks/debug-application-cluster/)

### 🎉 Déploiement Réussi !

Une fois le déploiement terminé, votre API sera accessible via :

- **URL publique** : `https://votre-domaine.com` (si configuré)
- **LoadBalancer IP** : `http://IP_EXTERNE` (si LoadBalancer activé)
- **Port-forward local** : `http://localhost:8080` (pour tests)

#### Endpoints disponibles :
- `GET /health` - Vérification de santé
- `POST /predict` - Prédiction de toxicité
- `GET /docs` - Documentation Swagger
- `GET /metrics` - Métriques Prometheus (optionnel)

---

> ⚡ **Tip Pro** : Utilisez le script `monitor-gcp.ps1` pour surveiller votre déploiement en temps réel et identifier rapidement les problèmes potentiels.
