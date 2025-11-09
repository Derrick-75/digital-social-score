# 🚀 Guide de Démarrage Rapide - MLOps

## Étapes pour lancer le pipeline MLOps

### 1️⃣ Installer les dépendances

```bash
pip install -r etape7-mlops/requirements.txt
```

### 2️⃣ Activer l'API Vertex AI

```bash
gcloud services enable aiplatform.googleapis.com --project=digitalsocialscoreapi
```

### 3️⃣ Uploader les données d'entraînement vers GCS

```bash
cd etape7-mlops
python upload_data_to_gcs.py --project-id digitalsocialscoreapi
```

**Résultat attendu :**
```
📤 Upload des données vers GCS...
   Bucket: digitalsocialscoreapi_cloudbuild
✅ Bucket existant: gs://digitalsocialscoreapi_cloudbuild
✅ Uploaded: etape1-anonymisation/data/raw/train_advanced.csv
   → gs://digitalsocialscoreapi_cloudbuild/data/train_advanced.csv
   Size: 2.45 MB
✅ Uploaded: etape1-anonymisation/data/raw/test_advanced.csv
   → gs://digitalsocialscoreapi_cloudbuild/data/test_advanced.csv
   Size: 0.61 MB

🎉 Upload terminé!
```

### 4️⃣ Déclencher le pipeline (modèle simple)

```bash
cd vertex_pipelines
python trigger_pipeline.py \
    --project-id digitalsocialscoreapi \
    --region europe-west1 \
    --model-type simple \
    --epochs 3
```

**Résultat attendu :**
```
🚀 Déclenchement du pipeline Vertex AI...
   Project: digitalsocialscoreapi
   Region: europe-west1
   Model Type: simple
   Epochs: 3
   Pipeline Root: gs://digitalsocialscoreapi_cloudbuild/vertex-pipelines
✅ Pipeline compilé
📤 Soumission du pipeline job: dss-ml-pipeline-simple-20241106_153045
✅ Pipeline soumis avec succès!
   Job Name: projects/.../locations/.../pipelineJobs/...
   Console URL: https://console.cloud.google.com/vertex-ai/pipelines/runs?project=digitalsocialscoreapi

💡 Suivez l'exécution dans la console Vertex AI Pipelines
```

### 5️⃣ Suivre l'exécution du pipeline

Ouvrir dans le navigateur :
```
https://console.cloud.google.com/vertex-ai/pipelines/runs?project=digitalsocialscoreapi
```

**Vous verrez :**
- 📋 Étape 1 : Préparation des données (en cours...)
- 🤖 Étape 2 : Entraînement modèle SIMPLE (en attente)
- 📊 Étape 3 : Évaluation du modèle (en attente)
- 🚀 Étape 4 : Déploiement (conditionnel)

**Durée estimée :**
- Modèle Simple : ~10-15 minutes
- Modèle BERT : ~30-45 minutes (avec GPU)

### 6️⃣ (Optionnel) Tester avec BERT

```bash
python trigger_pipeline.py \
    --project-id digitalsocialscoreapi \
    --region europe-west1 \
    --model-type bert \
    --epochs 5
```

---

## 🔧 Intégration avec Cloud Build (Automatique)

Pour automatiser le pipeline après chaque déploiement, ajoutez cette étape dans `cloudbuild.yaml` :

```yaml
# Étape 7 : Déclencher le pipeline MLOps (optionnel, décommenter pour activer)
# - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk:slim'
#   id: 'trigger-mlops-pipeline'
#   entrypoint: 'bash'
#   waitFor: ['smoke-tests']
#   args:
#     - '-c'
#     - |
#       pip install -r etape7-mlops/requirements.txt
#       cd etape7-mlops/vertex_pipelines
#       python trigger_pipeline.py \
#         --project-id $PROJECT_ID \
#         --region europe-west1 \
#         --model-type simple \
#         --epochs 3
```

**⚠️ Attention :** Cette étape entraînera le modèle à chaque push. Décommenter seulement si vous voulez un retraining automatique.

---

## 📊 Vérifier les résultats

### Dans la console Vertex AI

1. Aller sur : https://console.cloud.google.com/vertex-ai/pipelines/runs
2. Cliquer sur votre pipeline run
3. Vérifier :
   - ✅ **Étape 1 (Préparation)** : Logs montrent nombre de samples, ratio toxic, etc.
   - ✅ **Étape 2 (Entraînement)** : Logs montrent progression des epochs, loss, etc.
   - ✅ **Étape 3 (Évaluation)** : Métriques finales (F1, Accuracy, Precision, Recall)
   - ✅ **Étape 4 (Déploiement)** : Si F1 >= 0.75, modèle déployé vers GCS

### Métriques attendues

| Étape | Métrique | Valeur attendue |
|-------|----------|-----------------|
| Préparation | Nombre de samples | ~15,000-20,000 |
| Préparation | Ratio toxic | ~10-15% |
| Entraînement | Loss finale | < 0.5 |
| Évaluation | F1-Score | **≥ 0.75** |
| Évaluation | Accuracy | ≥ 0.80 |
| Déploiement | Should Deploy | **True** si F1 ≥ 0.75 |

---

## ❓ Dépannage

### "Permission denied" lors de l'upload GCS

```bash
# Authentifier avec gcloud
gcloud auth application-default login

# Ou utiliser un service account
gcloud auth activate-service-account --key-file=key.json
```

### "API not enabled"

```bash
# Activer toutes les APIs nécessaires
gcloud services enable aiplatform.googleapis.com \
    storage.googleapis.com \
    cloudbuild.googleapis.com \
    --project=digitalsocialscoreapi
```

### Pipeline bloqué sur "Pending"

- Vérifier les quotas Vertex AI : https://console.cloud.google.com/iam-admin/quotas
- Vérifier la région (doit être `europe-west1`)
- Vérifier que le bucket GCS existe et contient les données

---

## 🎯 Checklist de validation

- [ ] ✅ API Vertex AI activée
- [ ] ✅ Bucket GCS créé : `digitalsocialscoreapi_cloudbuild`
- [ ] ✅ Données uploadées : `train_advanced.csv` + `test_advanced.csv`
- [ ] ✅ Pipeline déclenché manuellement (modèle simple)
- [ ] ✅ Pipeline complété avec succès (toutes les étapes vertes)
- [ ] ✅ Métriques validées (F1 ≥ 0.75)
- [ ] ✅ Modèle déployé vers GCS (si F1 suffisant)
- [ ] 🔄 (Optionnel) Intégration Cloud Build configurée

---

**Temps total estimé :** 30-45 minutes (première exécution)

**Questions ?** Consultez le README principal : `etape7-mlops/README.md`
