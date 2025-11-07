# 🚀 Guide de Configuration Google Cloud Build

## 📋 Vue d'ensemble

Ce guide vous accompagne pour configurer **Google Cloud Build** et mettre en place un **pipeline CI/CD automatique** pour le projet Digital Social Score.

### Qu'est-ce qui sera automatisé ?

À chaque `git push` sur GitHub, le pipeline va :
1. ✅ Exécuter les tests unitaires
2. ✅ Construire l'image Docker
3. ✅ Pousser l'image sur Google Container Registry
4. ✅ Déployer automatiquement sur GKE
5. ✅ Vérifier que le déploiement fonctionne
6. ✅ Lancer des smoke tests (health check, metrics, API)

---

## 🎯 Prérequis

Avant de commencer, assurez-vous d'avoir :
- ✅ Un compte Google Cloud avec le projet `digitalsocialscoreapi`
- ✅ Le cluster GKE `dss-cluster` déployé (étape 3 terminée)
- ✅ L'API déjà fonctionnelle sur http://34.38.214.124
- ✅ Un repository GitHub avec votre code

---

## 📝 Étape 1 : Activer les APIs Google Cloud

### 1.1 Ouvrir Cloud Shell

1. Allez sur https://console.cloud.google.com
2. Cliquez sur l'icône **Cloud Shell** (en haut à droite)
3. Attendez que le terminal s'ouvre

### 1.2 Activer les APIs nécessaires

```bash
# Activer Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Activer Container Registry API
gcloud services enable containerregistry.googleapis.com

# Activer Kubernetes Engine API (normalement déjà fait)
gcloud services enable container.googleapis.com

# Vérifier que tout est activé
gcloud services list --enabled | grep -E "cloudbuild|container"
```

**Résultat attendu** :
```
cloudbuild.googleapis.com
containerregistry.googleapis.com
container.googleapis.com
```

---

## 🔗 Étape 2 : Connecter GitHub à Cloud Build

### 2.1 Accéder à la page Cloud Build

1. Dans la console GCP, allez dans **Menu ☰** → **Cloud Build** → **Triggers** (Déclencheurs)
2. OU directement : https://console.cloud.google.com/cloud-build/triggers

### 2.2 Connecter votre dépôt GitHub

1. Cliquez sur **"Connecter un dépôt"** ou **"Connect Repository"**
2. Sélectionnez **"GitHub (Cloud Build GitHub App)"**
3. Cliquez sur **"Continuer"**

### 2.3 Autoriser Google Cloud Build sur GitHub

1. Une fenêtre GitHub va s'ouvrir
2. **Connectez-vous à GitHub** si nécessaire
3. Sélectionnez votre compte GitHub
4. Cliquez sur **"Autoriser Google Cloud Build"**
5. **Important** : Sélectionnez le repository `digital-social-score`
6. Cliquez sur **"Install"** ou **"Installer"**

### 2.4 Sélectionner le dépôt dans Cloud Build

1. De retour dans la console GCP
2. Sélectionnez votre repository : **`<votre-username>/digital-social-score`**
3. **Cochez la case** "J'ai lu et j'accepte..."
4. Cliquez sur **"Connecter"**

---

## ⚙️ Étape 3 : Créer le Déclencheur (Trigger)

### 3.1 Configurer le déclencheur

Après avoir connecté le dépôt, configurez le trigger :

| Paramètre | Valeur |
|-----------|--------|
| **Nom** | `dss-api-ci-cd` |
| **Description** | Pipeline CI/CD automatique pour Digital Social Score API |
| **Type d'événement** | **Push vers une branche** |
| **Branche** | `^main$` (ou `^master$` selon votre branche principale) |
| **Configuration** | **Cloud Build configuration file (yaml or json)** |
| **Emplacement** | `cloudbuild.yaml` (racine du projet) |

### 3.2 Configuration avancée (optionnel)

Cliquez sur **"Afficher les variables de substitution incluses"** et vérifiez :

| Variable | Valeur |
|----------|--------|
| `$PROJECT_ID` | digitalsocialscoreapi |
| `$SHORT_SHA` | (auto) |
| `$BRANCH_NAME` | (auto) |

### 3.3 Créer le déclencheur

1. Cliquez sur **"Créer"** en bas de page
2. Vous devriez voir votre déclencheur dans la liste

---

## 🔐 Étape 4 : Configurer les Permissions

Cloud Build a besoin d'accéder à GKE pour déployer. Configurons les permissions.

### 4.1 Identifier le compte de service

```bash
# Récupérer le numéro de projet
PROJECT_NUMBER=$(gcloud projects describe digitalsocialscoreapi --format="value(projectNumber)")

# Afficher le compte de service Cloud Build
echo "Compte de service: ${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
```

### 4.2 Donner les permissions GKE

```bash
# Permission pour déployer sur GKE
gcloud projects add-iam-policy-binding digitalsocialscoreapi \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/container.developer"

# Permission pour lire les clusters
gcloud projects add-iam-policy-binding digitalsocialscoreapi \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/container.clusterViewer"
```

### 4.3 Configurer kubectl pour Cloud Build

```bash
# Donner accès au cluster GKE
gcloud container clusters get-credentials dss-cluster \
    --region=europe-west1 \
    --project=digitalsocialscoreapi

# Créer un role binding pour Cloud Build
kubectl create clusterrolebinding cloud-build-admin \
    --clusterrole=cluster-admin \
    --serviceaccount=default:default \
    --namespace=dss
```

---

## 🧪 Étape 5 : Tester le Pipeline

### 5.1 Vérifier le fichier cloudbuild.yaml

Le fichier `cloudbuild.yaml` doit être à la **racine de votre projet** :

```
digital-social-score/
├── cloudbuild.yaml       ← ICI (racine)
├── etape3-api/
├── etape5-load-testing/
└── ...
```

### 5.2 Pousser le code sur GitHub

```powershell
# Depuis le dossier digital-social-score
git add cloudbuild.yaml
git commit -m "feat: Ajout pipeline CI/CD avec Google Cloud Build"
git push origin main
```

### 5.3 Observer le build

1. Retournez sur **Cloud Build** → **Historique** : https://console.cloud.google.com/cloud-build/builds
2. Vous devriez voir un build en cours avec 6 étapes
3. Cliquez dessus pour voir les logs en temps réel

### 5.4 Résultat attendu

Le pipeline devrait :
- ✅ **Étape 1** : Tests unitaires (30s)
- ✅ **Étape 2** : Build Docker (2-3 min)
- ✅ **Étape 3** : Push image (30s)
- ✅ **Étape 4** : Déploiement GKE (1 min)
- ✅ **Étape 5** : Vérification rollout (2 min)
- ✅ **Étape 6** : Smoke tests (1 min)

**Durée totale** : ~7-10 minutes

---

## 🐛 Dépannage (Troubleshooting)

### Erreur : "Permission denied" lors du déploiement

**Cause** : Le compte de service Cloud Build n'a pas les droits sur GKE

**Solution** :
```bash
# Réexécuter la commande de permissions
PROJECT_NUMBER=$(gcloud projects describe digitalsocialscoreapi --format="value(projectNumber)")
gcloud projects add-iam-policy-binding digitalsocialscoreapi \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/container.admin"
```

### Erreur : "Cluster not found"

**Cause** : Le nom du cluster ou la région ne correspond pas

**Solution** : Vérifiez dans `cloudbuild.yaml` :
```yaml
env:
  - 'CLOUDSDK_COMPUTE_REGION=europe-west1'    # ← Votre région
  - 'CLOUDSDK_CONTAINER_CLUSTER=dss-cluster'  # ← Votre cluster
```

### Erreur : Tests échouent

**Cause** : Le fichier de tests n'existe pas ou a un problème

**Solution** :
```bash
# Vérifier que le fichier existe
ls etape3-api/tests/test_api.py

# Tester en local
cd etape3-api
pytest tests/test_api.py -v
```

### Erreur : Smoke tests échouent

**Cause** : L'IP externe a changé ou le service n'est pas prêt

**Solution** : Mettez à jour l'IP dans `cloudbuild.yaml` (ligne 107) :
```yaml
curl -f http://VOTRE_NOUVELLE_IP/health || exit 1
```

---

## 📊 Étape 6 : Monitorer les Builds

### 6.1 Voir l'historique

- **Console** : https://console.cloud.google.com/cloud-build/builds
- Filtrer par branche, statut (SUCCESS, FAILURE)
- Télécharger les logs

### 6.2 Configurer les notifications (optionnel)

1. Allez dans **Cloud Build** → **Settings**
2. Activez **"Email notifications"**
3. Vous recevrez un email à chaque build (succès ou échec)

### 6.3 Badges GitHub (optionnel)

Ajoutez un badge dans votre `README.md` :

```markdown
[![Cloud Build Status](https://storage.googleapis.com/digitalsocialscoreapi-badges/builds/digital-social-score/branches/main.svg)](https://console.cloud.google.com/cloud-build/builds?project=digitalsocialscoreapi)
```

---

## 🎯 Prochaines Étapes (MLOps)

Maintenant que le CI/CD est en place, vous pouvez ajouter :

### 1. Tests de régression du modèle
```yaml
- name: 'python:3.10-slim'
  id: 'test-model-quality'
  args:
    - 'pytest'
    - 'etape2-modele-ia/tests/test_model_accuracy.py'
```

### 2. Analyse de code (linting)
```yaml
- name: 'python:3.10-slim'
  id: 'lint-code'
  args:
    - 'pylint'
    - 'etape3-api/app/'
```

### 3. Scan de sécurité
```yaml
- name: 'gcr.io/cloud-builders/gcloud'
  id: 'security-scan'
  args:
    - 'container'
    - 'images'
    - 'scan'
    - 'gcr.io/$PROJECT_ID/dss-api:$SHORT_SHA'
```

### 4. Tests de charge automatiques
```yaml
- name: 'locustio/locust'
  id: 'load-tests'
  args:
    - '-f'
    - 'etape5-load-testing/locustfile.py'
    - '--headless'
    - '--users'
    - '50'
    - '--run-time'
    - '2m'
```

---

## 📝 Résumé des Commandes

### Configuration initiale (une seule fois)
```bash
# Activer les APIs
gcloud services enable cloudbuild.googleapis.com containerregistry.googleapis.com

# Configurer les permissions
PROJECT_NUMBER=$(gcloud projects describe digitalsocialscoreapi --format="value(projectNumber)")
gcloud projects add-iam-policy-binding digitalsocialscoreapi \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/container.developer"
```

### Workflow quotidien
```powershell
# 1. Modifier le code
# 2. Tester en local (optionnel)
pytest etape3-api/tests/

# 3. Commit et push
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push origin main

# 4. Observer le build sur GCP
# https://console.cloud.google.com/cloud-build/builds
```

---

## ✅ Checklist de Validation

- [ ] APIs Cloud Build et Container Registry activées
- [ ] Repository GitHub connecté à Cloud Build
- [ ] Déclencheur `dss-api-ci-cd` créé
- [ ] Permissions configurées pour le compte de service
- [ ] Fichier `cloudbuild.yaml` à la racine du projet
- [ ] Premier build réussi (toutes les étapes en vert)
- [ ] L'API est toujours accessible après le déploiement
- [ ] Les smoke tests passent

---

## 🎓 Pour Aller Plus Loin

### Documentation officielle
- [Cloud Build Quickstart](https://cloud.google.com/build/docs/quickstart-build)
- [Cloud Build avec GKE](https://cloud.google.com/build/docs/deploying-builds/deploy-gke)
- [Cloud Build Triggers](https://cloud.google.com/build/docs/automating-builds/create-manage-triggers)

### Exemples avancés
- [Multi-stage builds](https://cloud.google.com/build/docs/optimize-builds/docker-best-practices)
- [Parallel builds](https://cloud.google.com/build/docs/configuring-builds/create-basic-configuration#parallel-builds)
- [Build caching](https://cloud.google.com/build/docs/optimize-builds/speeding-up-builds)

---

**Date de création** : 07/11/2025  
**Version** : 1.0  
**Auteur** : Digital Social Score Team
