# Commandes Utiles - Google Cloud Build

## 📋 Configuration Initiale

### Activer les APIs nécessaires
```bash
# Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Container Registry API  
gcloud services enable containerregistry.googleapis.com

# Kubernetes Engine API
gcloud services enable container.googleapis.com

# Vérifier les APIs activées
gcloud services list --enabled | grep -E "build|container"
```

### Configurer le projet
```bash
# Définir le projet par défaut
gcloud config set project digitalsocialscoreapi

# Vérifier le projet actuel
gcloud config get-value project

# Définir la région par défaut
gcloud config set compute/region europe-west1
```

---

## 🔐 Permissions

### Obtenir le numéro de projet
```bash
PROJECT_NUMBER=$(gcloud projects describe digitalsocialscoreapi --format="value(projectNumber)")
echo "Numéro de projet: $PROJECT_NUMBER"
```

### Configurer les permissions pour Cloud Build
```bash
# Permission pour déployer sur GKE
gcloud projects add-iam-policy-binding digitalsocialscoreapi \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/container.developer"

# Permission pour gérer les clusters
gcloud projects add-iam-policy-binding digitalsocialscoreapi \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/container.clusterAdmin"

# Permission pour voir les clusters
gcloud projects add-iam-policy-binding digitalsocialscoreapi \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/container.clusterViewer"

# Permission pour pousser des images
gcloud projects add-iam-policy-binding digitalsocialscoreapi \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/storage.admin"
```

### Vérifier les permissions
```bash
gcloud projects get-iam-policy digitalsocialscoreapi \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
```

---

## 🚀 Gestion des Builds

### Lancer un build manuellement
```bash
# Build avec le fichier cloudbuild.yaml
gcloud builds submit --config=cloudbuild.yaml .

# Build avec un tag spécifique
gcloud builds submit --config=cloudbuild.yaml --substitutions=TAG_NAME=v1.0.0 .

# Build avec timeout personnalisé
gcloud builds submit --config=cloudbuild.yaml --timeout=30m .
```

### Lister les builds
```bash
# Les 10 derniers builds
gcloud builds list --limit=10

# Builds d'aujourd'hui
gcloud builds list --filter="createTime>$(date -u -d '1 day ago' '+%Y-%m-%dT%H:%M:%S')"

# Builds échoués
gcloud builds list --filter="status=FAILURE"

# Builds réussis
gcloud builds list --filter="status=SUCCESS"

# Format détaillé
gcloud builds list --format="table(id,createTime,duration,status,source.repoSource.branchName)"
```

### Voir les détails d'un build
```bash
# Par ID
gcloud builds describe BUILD_ID

# Format JSON
gcloud builds describe BUILD_ID --format=json

# Uniquement le status
gcloud builds describe BUILD_ID --format="value(status)"
```

### Voir les logs d'un build
```bash
# Logs complets
gcloud builds log BUILD_ID

# Suivre les logs en temps réel
gcloud builds log BUILD_ID --stream

# Sauvegarder les logs
gcloud builds log BUILD_ID > build_logs.txt
```

### Annuler un build en cours
```bash
gcloud builds cancel BUILD_ID
```

---

## 🔧 Gestion des Triggers

### Lister les triggers
```bash
# Tous les triggers
gcloud builds triggers list

# Format tableau
gcloud builds triggers list --format="table(name,description,triggerTemplate.branchName)"
```

### Créer un trigger (CLI)
```bash
gcloud builds triggers create github \
    --name="dss-api-ci-cd" \
    --description="Pipeline CI/CD pour Digital Social Score API" \
    --repo-name="digital-social-score" \
    --repo-owner="VOTRE_USERNAME" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild.yaml"
```

### Voir les détails d'un trigger
```bash
gcloud builds triggers describe TRIGGER_ID
```

### Exécuter un trigger manuellement
```bash
gcloud builds triggers run TRIGGER_NAME --branch=main
```

### Supprimer un trigger
```bash
gcloud builds triggers delete TRIGGER_NAME
```

### Désactiver/Activer un trigger
```bash
# Désactiver
gcloud builds triggers update TRIGGER_NAME --disabled

# Réactiver
gcloud builds triggers update TRIGGER_NAME --no-disabled
```

---

## 🖼️ Gestion des Images (GCR)

### Lister les images
```bash
# Toutes les images
gcloud container images list --repository=gcr.io/digitalsocialscoreapi

# Images d'un dépôt spécifique
gcloud container images list-tags gcr.io/digitalsocialscoreapi/dss-api

# Avec détails (taille, date)
gcloud container images list-tags gcr.io/digitalsocialscoreapi/dss-api \
    --format="table(tags,digest,timestamp)"
```

### Supprimer une image
```bash
# Par tag
gcloud container images delete gcr.io/digitalsocialscoreapi/dss-api:TAG

# Par digest
gcloud container images delete gcr.io/digitalsocialscoreapi/dss-api@sha256:DIGEST

# Supprimer toutes les images non taguées
gcloud container images list-tags gcr.io/digitalsocialscoreapi/dss-api \
    --filter='-tags:*' --format="get(digest)" --limit=unlimited | \
    xargs -I {} gcloud container images delete "gcr.io/digitalsocialscoreapi/dss-api@sha256:{}" --quiet
```

### Voir les détails d'une image
```bash
gcloud container images describe gcr.io/digitalsocialscoreapi/dss-api:latest
```

---

## ☸️ Déploiement GKE

### Se connecter au cluster
```bash
gcloud container clusters get-credentials dss-cluster \
    --region=europe-west1 \
    --project=digitalsocialscoreapi
```

### Vérifier le déploiement
```bash
# Status du déploiement
kubectl get deployment dss-api -n dss

# Pods en cours
kubectl get pods -n dss

# Historique des rollouts
kubectl rollout history deployment/dss-api -n dss

# Status du rollout en cours
kubectl rollout status deployment/dss-api -n dss
```

### Rollback manuel
```bash
# Revenir à la version précédente
kubectl rollout undo deployment/dss-api -n dss

# Revenir à une revision spécifique
kubectl rollout undo deployment/dss-api -n dss --to-revision=2
```

---

## 📊 Monitoring et Logs

### Voir les logs de build
```bash
# Logs du dernier build
gcloud builds log $(gcloud builds list --limit=1 --format="value(id)")

# Logs filtrés
gcloud builds log BUILD_ID | grep ERROR
```

### Statistiques des builds
```bash
# Nombre de builds par status
gcloud builds list --format="value(status)" | sort | uniq -c

# Durée moyenne des builds réussis
gcloud builds list --filter="status=SUCCESS" --format="value(duration)" | \
    awk '{sum+=$1; count++} END {print "Moyenne:", sum/count, "secondes"}'
```

### Alertes et notifications
```bash
# Créer une notification Pub/Sub
gcloud builds triggers update TRIGGER_NAME \
    --subscription=projects/digitalsocialscoreapi/subscriptions/build-notifications
```

---

## 🧪 Tests et Debugging

### Tester cloudbuild.yaml localement
```bash
# Installer cloud-build-local (une seule fois)
gcloud components install cloud-build-local

# Exécuter localement
cloud-build-local --config=cloudbuild.yaml --dryrun=false .
```

### Valider le fichier cloudbuild.yaml
```bash
# Syntaxe YAML
yamllint cloudbuild.yaml

# Validation avec gcloud (dry-run)
gcloud builds submit --config=cloudbuild.yaml --no-source --dry-run
```

### Debug d'un step spécifique
```bash
# Ajouter dans cloudbuild.yaml
steps:
  - name: 'bash'
    id: 'debug'
    script: |
      echo "DEBUG: Variables disponibles"
      echo "PROJECT_ID: $PROJECT_ID"
      echo "SHORT_SHA: $SHORT_SHA"
      echo "BRANCH_NAME: $BRANCH_NAME"
      ls -la
```

---

## 🔄 Workflows Courants

### Workflow : Nouveau déploiement
```bash
# 1. Modifier le code
vim etape3-api/app/main.py

# 2. Tester localement
cd etape3-api && pytest tests/

# 3. Commit et push
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push origin main

# 4. Suivre le build
gcloud builds list --ongoing --limit=1 --format="table(id,status,source.repoSource.branchName)"

# 5. Voir les logs en temps réel
BUILD_ID=$(gcloud builds list --ongoing --limit=1 --format="value(id)")
gcloud builds log $BUILD_ID --stream
```

### Workflow : Rollback d'urgence
```bash
# 1. Identifier la version stable
kubectl rollout history deployment/dss-api -n dss

# 2. Rollback
kubectl rollout undo deployment/dss-api -n dss --to-revision=STABLE_REVISION

# 3. Vérifier
kubectl get pods -n dss -w
```

### Workflow : Nettoyer les anciennes images
```bash
# Garder seulement les 10 dernières images
gcloud container images list-tags gcr.io/digitalsocialscoreapi/dss-api \
    --sort-by=~TIMESTAMP --limit=999 --format="get(digest)" | \
    tail -n +11 | \
    xargs -I {} gcloud container images delete "gcr.io/digitalsocialscoreapi/dss-api@sha256:{}" --quiet
```

---

## 📚 Ressources

### Documentation
- [Cloud Build](https://cloud.google.com/build/docs)
- [Build Config Reference](https://cloud.google.com/build/docs/build-config-file-schema)
- [gcloud builds](https://cloud.google.com/sdk/gcloud/reference/builds)

### Liens Utiles
- [Console Cloud Build](https://console.cloud.google.com/cloud-build/builds)
- [Console GCR](https://console.cloud.google.com/gcr/images/digitalsocialscoreapi)
- [Console GKE](https://console.cloud.google.com/kubernetes/workload)

---

**Date de mise à jour** : 07/11/2025
