# 🚀 Guide de Démarrage Rapide - MLOps avec Vertex AI

## 📋 Vue d'ensemble

Ce dossier contient le pipeline MLOps complet pour automatiser l'entraînement et le déploiement du modèle de détection de toxicité.

### Architecture du pipeline

```
1. Préparation données → 2. Entraînement → 3. Évaluation → 4. Déploiement
        ↓                      ↓                  ↓              ↓
   Anonymisation          BERT/Simple        F1-Score       Si F1 > 0.75
   Nettoyage             Fine-tuning         Accuracy       → Deploy auto
```

---

## ⚡ Démarrage rapide (5 minutes)

### 1. Installer les dépendances

```bash
cd etape7-mlops
pip install -r requirements.txt
```

### 2. Activer les APIs nécessaires

```bash
python setup_vertex_ai.py
```

### 3. Uploader les données d'entraînement

```bash
python upload_training_data.py
```

### 4. Compiler le pipeline

```bash
python compile_pipeline.py
```

### 5. Lancer le pipeline

```bash
python trigger_pipeline.py --model-type simple
```

---

## 📂 Structure des fichiers

```
etape7-mlops/
├── vertex_pipelines/
│   ├── components/
│   │   ├── prepare_data.py          # Composant de préparation des données
│   │   ├── train_model.py           # Composant d'entraînement
│   │   └── evaluate_model.py        # Composant d'évaluation
│   ├── pipeline_definition.py       # Définition du pipeline complet
│   └── ml_pipeline.json             # Pipeline compilé (généré)
├── compile_pipeline.py              # Script de compilation
├── trigger_pipeline.py              # Script de déclenchement
├── upload_training_data.py          # Upload données vers GCS
├── setup_vertex_ai.py               # Configuration initiale
├── requirements.txt                 # Dépendances Python
└── README.md                        # Ce fichier
```

---

## 🔧 Configuration

### Variables d'environnement

Le pipeline utilise ces configurations par défaut :

```python
PROJECT_ID = "digitalsocialscoreapi"
REGION = "europe-west1"
PIPELINE_ROOT = "gs://digitalsocialscoreapi_cloudbuild/vertex-pipelines"
```

### Paramètres du pipeline

Vous pouvez personnaliser l'entraînement :

```bash
# Modèle simple (rapide, ~5-10 min)
python trigger_pipeline.py --model-type simple

# Modèle BERT (lent, ~30-60 min, meilleure performance)
python trigger_pipeline.py --model-type bert
```

---

## 📊 Suivre l'exécution

Une fois le pipeline lancé, vous pouvez suivre son exécution :

**Console Vertex AI :**
https://console.cloud.google.com/vertex-ai/pipelines

**Logs Cloud Logging :**
https://console.cloud.google.com/logs

---

## 🔄 Intégration avec Cloud Build

Le pipeline peut être déclenché automatiquement par Cloud Build.

### Option 1 : Déclenchement manuel

Ajoutez dans `cloudbuild.yaml` :

```yaml
# Étape optionnelle : Lancer le pipeline MLOps
- name: 'python:3.10-slim'
  id: 'trigger-ml-pipeline'
  entrypoint: 'bash'
  args:
    - '-c'
    - |
      pip install -q kfp google-cloud-aiplatform
      python etape7-mlops/trigger_pipeline.py --model-type simple
  waitFor: ['smoke-tests']
```

### Option 2 : Déclenchement hebdomadaire

Créez un Cloud Scheduler qui lance le pipeline chaque semaine :

```bash
gcloud scheduler jobs create http ml-pipeline-weekly \
  --location=europe-west1 \
  --schedule="0 2 * * 0" \
  --uri="https://europe-west1-aiplatform.googleapis.com/v1/projects/digitalsocialscoreapi/locations/europe-west1/pipelineJobs" \
  --message-body-from-file=pipeline_trigger.json
```

---

## 🧪 Tests

### Tester la compilation

```bash
python compile_pipeline.py
# Vérifie que vertex_pipelines/ml_pipeline.json est créé
```

### Tester l'upload des données

```bash
python upload_training_data.py --dry-run
```

### Tester un composant individuellement

```bash
cd vertex_pipelines/components
python prepare_data.py  # Test local
```

---

## 📈 Monitoring

Le pipeline génère des métriques à chaque exécution :

- **F1-Score** : Performance du modèle
- **Accuracy** : Précision globale
- **Temps d'entraînement** : Durée totale
- **Taille du modèle** : Espace disque

Ces métriques sont stockées dans :
- Vertex AI Metadata Store
- GCS : `gs://digitalsocialscoreapi_cloudbuild/vertex-pipelines/metrics/`

---

## 🚨 Troubleshooting

### Erreur : "Permission denied"

Assurez-vous que le compte de service a les permissions :

```bash
gcloud projects add-iam-policy-binding digitalsocialscoreapi \
  --member="serviceAccount:YOUR_SA@digitalsocialscoreapi.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### Erreur : "Bucket not found"

Créez le bucket GCS :

```bash
gsutil mb -l europe-west1 gs://digitalsocialscoreapi_cloudbuild
```

### Pipeline échoue à l'entraînement

Vérifiez les logs détaillés dans Vertex AI :

```bash
gcloud ai custom-jobs describe JOB_ID \
  --region=europe-west1 \
  --project=digitalsocialscoreapi
```

---

## 📚 Ressources

- [Vertex AI Pipelines Documentation](https://cloud.google.com/vertex-ai/docs/pipelines)
- [Kubeflow Pipelines SDK](https://www.kubeflow.org/docs/components/pipelines/)
- [MLOps Best Practices](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)

---

## 🎯 Prochaines étapes

1. ✅ Pipeline de base fonctionnel
2. 🔄 Ajout du monitoring en production
3. 🔄 A/B testing entre modèles
4. 🔄 Détection de drift des données
5. 🔄 Réentraînement automatique conditionnel

---

**Date de création :** 8 novembre 2025  
**Version :** 1.0  
**Auteur :** Digital Social Score Team
