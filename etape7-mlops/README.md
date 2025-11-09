# Étape 7 : MLOps avec Vertex AI Pipelines

## 🎯 Objectif

Automatiser complètement le cycle de vie du modèle ML :
- ✅ Préparation automatique des données
- ✅ Entraînement automatisé (BERT ou Simple)
- ✅ Évaluation et validation
- ✅ Déploiement conditionnel basé sur les performances

## 🏗️ Architecture du Pipeline

```
┌─────────────────────┐
│  1. Préparation     │
│     des données     │
│  - Nettoyage        │
│  - Anonymisation    │
│  - Statistiques     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. Entraînement    │
│     du modèle       │
│  - BERT ou Simple   │
│  - Hyperparamètres  │
│  - Sauvegarde       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. Évaluation      │
│  - Métriques (F1)   │
│  - Validation       │
│  - Décision deploy  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  4. Déploiement     │
│     (conditionnel)  │
│  - Si F1 >= 0.75    │
│  - Upload GCS       │
└─────────────────────┘
```

## 📁 Structure des fichiers

```
etape7-mlops/
├── requirements.txt                    # Dépendances MLOps
├── README.md                          # Cette documentation
└── vertex_pipelines/
    ├── components/                    # Composants KFP
    │   ├── prepare_data.py           # Préparation des données
    │   ├── train_model.py            # Entraînement du modèle
    │   └── evaluate_model.py         # Évaluation du modèle
    ├── pipeline_definition.py         # Définition du pipeline complet
    └── trigger_pipeline.py            # Script de déclenchement
```

## 🚀 Utilisation

### 1. Prérequis

```bash
# Installer les dépendances
pip install -r requirements.txt

# Activer l'API Vertex AI
gcloud services enable aiplatform.googleapis.com

# Créer un bucket GCS pour les artefacts (si pas déjà fait)
gsutil mb -l europe-west1 gs://digitalsocialscoreapi_cloudbuild
```

### 2. Uploader les données d'entraînement sur GCS

```bash
# Copier les datasets vers GCS
gsutil cp etape1-anonymisation/data/raw/train_advanced.csv \
    gs://digitalsocialscoreapi_cloudbuild/data/

gsutil cp etape1-anonymisation/data/raw/test_advanced.csv \
    gs://digitalsocialscoreapi_cloudbuild/data/
```

### 3. Déclencher manuellement le pipeline

```bash
cd etape7-mlops/vertex_pipelines

# Entraîner un modèle simple
python trigger_pipeline.py \
    --project-id digitalsocialscoreapi \
    --region europe-west1 \
    --model-type simple \
    --epochs 3

# Entraîner un modèle BERT
python trigger_pipeline.py \
    --project-id digitalsocialscoreapi \
    --region europe-west1 \
    --model-type bert \
    --epochs 5
```

### 4. Intégration avec Cloud Build (Automatique)

Le pipeline sera automatiquement déclenché après chaque déploiement réussi via Cloud Build.

**Ajout dans `cloudbuild.yaml` :**

```yaml
# Étape 7 : Déclencher le pipeline MLOps (optionnel)
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk:slim'
  id: 'trigger-mlops-pipeline'
  entrypoint: 'bash'
  waitFor: ['smoke-tests']
  args:
    - '-c'
    - |
      pip install -r etape7-mlops/requirements.txt
      cd etape7-mlops/vertex_pipelines
      python trigger_pipeline.py \
        --project-id $PROJECT_ID \
        --region europe-west1 \
        --model-type simple \
        --epochs 3
```

## 📊 Monitoring du Pipeline

### Console Vertex AI

1. Ouvrir : https://console.cloud.google.com/vertex-ai/pipelines/runs?project=digitalsocialscoreapi
2. Sélectionner votre pipeline run
3. Visualiser :
   - ✅ État de chaque étape
   - 📈 Métriques d'entraînement
   - 📊 Résultats d'évaluation
   - 🚀 Décision de déploiement

### Logs Cloud Logging

```bash
# Voir les logs du pipeline
gcloud logging read "resource.type=ml_job" --limit 50 --format json
```

## 🔧 Configuration des Paramètres

Le pipeline accepte plusieurs paramètres configurables :

| Paramètre | Description | Défaut |
|-----------|-------------|--------|
| `raw_data_gcs_path` | Chemin GCS des données d'entraînement | `gs://.../train_advanced.csv` |
| `test_data_gcs_path` | Chemin GCS des données de test | `gs://.../test_advanced.csv` |
| `model_type` | Type de modèle (`simple` ou `bert`) | `simple` |
| `epochs` | Nombre d'époques d'entraînement | `3` |
| `batch_size` | Taille des batches | `16` |
| `learning_rate` | Taux d'apprentissage | `2e-5` |
| `min_f1_threshold` | Seuil F1 pour déployer | `0.75` |

**Modifier dans `trigger_pipeline.py` :**

```python
pipeline_parameters = {
    "epochs": 10,           # Plus d'époques
    "batch_size": 32,       # Batches plus grands
    "min_f1_threshold": 0.80  # Seuil plus élevé
}
```

## 🎓 Composants du Pipeline

### 1. `prepare_data_component`

**Fonction :** Nettoie et anonymise les données

**Inputs :**
- `raw_data_path` : Chemin vers les données brutes (CSV)

**Outputs :**
- `output_dataset` : Dataset nettoyé et anonymisé

**Actions :**
- Suppression des doublons
- Gestion des valeurs manquantes
- Anonymisation des emails (SHA-256)
- Calcul des statistiques

### 2. `train_model_component`

**Fonction :** Entraîne le modèle ML

**Inputs :**
- `input_dataset` : Dataset préparé
- `model_type` : Type de modèle ("simple" ou "bert")
- `epochs`, `batch_size`, `learning_rate`

**Outputs :**
- `output_model` : Modèle entraîné

**Modèles supportés :**
- **Simple :** TF-IDF + Logistic Regression
- **BERT :** BERT fine-tuned sur les données

### 3. `evaluate_model_component`

**Fonction :** Évalue les performances du modèle

**Inputs :**
- `test_dataset` : Dataset de test
- `trained_model` : Modèle entraîné
- `min_f1_threshold` : Seuil F1 minimum

**Outputs :**
- `f1_score` : Score F1 obtenu
- `should_deploy` : Boolean (déployer ou non)

**Métriques calculées :**
- Accuracy, Precision, Recall, F1-Score
- AUC-ROC
- Matrice de confusion

### 4. `deploy_model_component`

**Fonction :** Déploie le modèle si performances suffisantes

**Condition :** `should_deploy == True` (F1 >= threshold)

**Actions :**
- Upload du modèle vers GCS
- Mise à jour du pointeur `active_model.json`
- Versioning avec timestamp

## 📈 Métriques de Référence

| Modèle | F1-Score | Précision | Rappel | AUC-ROC |
|--------|----------|-----------|--------|---------|
| Simple (baseline) | 0.75+ | 0.73+ | 0.77+ | 0.82+ |
| BERT (actuel) | **0.8134** | 0.79 | 0.84 | 0.89 |
| **Objectif MLOps** | **≥ 0.75** | ≥ 0.70 | ≥ 0.70 | ≥ 0.80 |

## 🛠️ Dépannage

### Pipeline ne démarre pas

```bash
# Vérifier que l'API est activée
gcloud services list --enabled | grep aiplatform

# Vérifier les permissions
gcloud projects get-iam-policy digitalsocialscoreapi
```

### Erreur "Bucket not found"

```bash
# Créer le bucket s'il n'existe pas
gsutil mb -l europe-west1 gs://digitalsocialscoreapi_cloudbuild

# Vérifier les permissions
gsutil iam get gs://digitalsocialscoreapi_cloudbuild
```

### Composant échoue

```bash
# Voir les logs détaillés dans la console Vertex AI
# Ou via gcloud :
gcloud ai custom-jobs list --region=europe-west1
gcloud ai custom-jobs describe JOB_ID --region=europe-west1
```

## 🔄 CI/CD Complet

Une fois intégré à Cloud Build, le workflow complet devient :

```
1. git push → code_godson
2. Cloud Build triggered
3. Tests unitaires (8/8 passés)
4. Build Docker image
5. Push to GCR
6. Deploy to GKE
7. Smoke tests
8. ✨ Déclenche pipeline Vertex AI
9. Entraînement automatique
10. Évaluation automatique
11. Déploiement conditionnel du nouveau modèle
```

## 📚 Ressources

- [Vertex AI Pipelines Documentation](https://cloud.google.com/vertex-ai/docs/pipelines)
- [Kubeflow Pipelines SDK](https://www.kubeflow.org/docs/components/pipelines/)
- [ML Pipeline Best Practices](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)

## 🎉 Prochaines Étapes

- [ ] Exécution manuelle du pipeline de test
- [ ] Intégration avec Cloud Build
- [ ] Monitoring des métriques dans Cloud Monitoring
- [ ] Ajout de Cloud Scheduler pour retraining périodique
- [ ] Implémentation de A/B testing entre modèles
- [ ] Ajout de drift detection sur les données

---

**Auteur :** Digital Social Score Team  
**Date :** 2024  
**Version :** 1.0
