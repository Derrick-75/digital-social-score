# 🎯 Guide d'Implémentation MLOps - Digital Social Score

## 📌 Vue Synthétique

Cette architecture MLOps permet l'**entraînement automatique et le déploiement conditionnel** du modèle BERT de détection de toxicité.

---

## 🏗️ Composants Principaux

### 1️⃣ **Vertex AI Pipelines** (Orchestration)
- **Rôle** : Orchestrer les 3 étapes du pipeline MLOps
- **Technologie** : Kubeflow Pipelines (KFP 2.14.6)
- **Hébergement** : Vertex AI (GCP)

### 2️⃣ **Cloud Storage** (Stockage)
- **Rôle** : Stocker données, modèles, artefacts
- **Bucket** : `gs://digitalsocialscoreapi_cloudbuild/`
- **Durabilité** : 99.999999999% (11 nines)

### 3️⃣ **Container Registry** (Images)
- **Rôle** : Images Docker des composants pipeline
- **Base Image** : `python:3.10-slim`
- **Auto-build** : Oui (par Vertex AI)

### 4️⃣ **API FastAPI** (Production)
- **Rôle** : Servir les prédictions en temps réel
- **Hébergement** : GKE (Kubernetes)
- **Scalabilité** : Auto-scaling horizontal

### 5️⃣ **Monitoring** (Observabilité)
- **Prometheus** : Métriques applicatives
- **Cloud Logging** : Logs centralisés
- **Vertex AI Metadata** : Tracking des exécutions

---

## 🔄 Flux de Données

```
┌─────────────────┐
│  Données Brutes │  train.csv (159k lignes)
│   (GCS)         │  test.csv (153k lignes)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  PIPELINE VERTEX AI (Exécution ~45-60 min)              │
│                                                          │
│  ┌──────────────────────────────────────────┐          │
│  │ ÉTAPE 1: prepare_data_op (5-10 min)      │          │
│  │ • Télécharge train.csv depuis GCS        │          │
│  │ • Charge modèle spaCy (en_core_web_sm)   │          │
│  │ • Détecte entités (PERSON, ORG, GPE...)  │          │
│  │ • Anonymise avec hash SHA-256            │          │
│  │ • Nettoie données (remove NaN, courts)   │          │
│  │ OUTPUT: anonymized_data.csv              │          │
│  └──────────────┬───────────────────────────┘          │
│                 │                                        │
│                 ▼                                        │
│  ┌──────────────────────────────────────────┐          │
│  │ ÉTAPE 2: train_model_op (30-45 min)      │          │
│  │ • Charge anonymized_data.csv             │          │
│  │ • Split train/val (80/20 stratifié)      │          │
│  │ • Tokenize avec BERT tokenizer           │          │
│  │ • Fine-tune bert-base-uncased (2 epochs) │          │
│  │ • Évalue sur validation set              │          │
│  │ OUTPUT: model_output/ (BERT + tokenizer) │          │
│  └──────────────┬───────────────────────────┘          │
│                 │                                        │
│                 ▼                                        │
│  ┌──────────────────────────────────────────┐          │
│  │ ÉTAPE 3: evaluate_and_decide_op (5-10m)  │          │
│  │ • Charge test.csv depuis GCS             │          │
│  │ • Charge model_output de l'étape 2       │          │
│  │ • Prédit sur test set (153k samples)     │          │
│  │ • Calcule F1, Accuracy, Precision, Recall│          │
│  │ • Compare F1 avec modèle actuel          │          │
│  │ DÉCISION:                                 │          │
│  │   ✅ if F1_new - F1_current >= 0.02:     │          │
│  │      → should_deploy = True              │          │
│  │   ❌ else:                                │          │
│  │      → should_deploy = False             │          │
│  │ OUTPUT: should_deploy, new_f1_score      │          │
│  └──────────────┬───────────────────────────┘          │
│                 │                                        │
└─────────────────┼────────────────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │ should_deploy? │
         └────┬───────┬───┘
              │       │
        YES ──┘       └── NO
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌──────────────┐
│ Déploiement API │  │  Archivage   │
│  (Production)   │  │   Modèle     │
└─────────────────┘  └──────────────┘
         │
         ▼
┌─────────────────┐
│  API FastAPI    │
│  • GET /health  │
│  • POST /predict│
│  • GET /metrics │
└─────────────────┘
         │
         ▼
   ┌──────────┐
   │ Utilisateurs
   └──────────┘
```

---

## 📊 Données et Formats

### **Données d'Entrée** (GCS)

**train.csv** (159,571 lignes, 61.68 MB)
```csv
comment_text,toxic
"This is a normal comment",0
"You are stupid idiot!",1
...
```

**test.csv** (153,164 lignes, 55.54 MB)
```csv
comment_text,toxic
"Another comment here",0
"Offensive content...",1
...
```

### **Données Anonymisées** (Après Étape 1)

```csv
text_anonymized,toxic
"This is a normal comment",0
"You are [PERSON_a3f8d2e1] idiot!",1
"[ORG_b7c9a4f3] is located in [GPE_e2d1f8b4]",0
"Contact me at [EMAIL]",0
...
```

### **Modèle Sauvegardé** (Après Étape 2)

```
model_output/
├── config.json              # Configuration BERT
├── pytorch_model.bin        # Poids du modèle (420 MB)
├── tokenizer_config.json    # Config tokenizer
├── vocab.txt                # Vocabulaire
├── special_tokens_map.json  # Tokens spéciaux
└── metadata.json            # Métadonnées custom
    {
      "model_name": "bert-base-uncased",
      "epochs": 2,
      "learning_rate": 2e-05,
      "batch_size": 16,
      "accuracy": 0.9234,
      "f1_score": 0.8567,
      "num_train_samples": 127656,
      "num_val_samples": 31914
    }
```

### **Rapport d'Évaluation** (Après Étape 3)

```json
{
  "accuracy": 0.9301,
  "f1_score": 0.8723,
  "precision": 0.8912,
  "recall": 0.8541,
  "current_f1": 0.8500,
  "improvement": 0.0223,
  "improvement_pct": 2.62,
  "should_deploy": true,
  "confusion_matrix": [[135201, 2341], [1832, 13790]],
  "classification_report": "..."
}
```

---

## ⚙️ Configuration & Paramètres

### **Variables d'Environnement**

```bash
# GCP Configuration
export PROJECT_ID="digitalsocialscoreapi"
export PROJECT_NUMBER="24274638091"
export REGION="europe-west1"
export SERVICE_ACCOUNT="24274638091-compute@developer.gserviceaccount.com"

# GCS Paths
export BUCKET="gs://digitalsocialscoreapi_cloudbuild"
export TRAIN_DATA="${BUCKET}/data/train.csv"
export TEST_DATA="${BUCKET}/data/test.csv"
export PIPELINE_ROOT="${BUCKET}/vertex-pipelines"

# Pipeline Parameters
export EPOCHS=2
export LEARNING_RATE=0.00002
export BATCH_SIZE=16
export CURRENT_MODEL_F1=0.50
export IMPROVEMENT_THRESHOLD=0.02
```

### **Paramètres Modifiables**

| Paramètre | Valeur Actuelle | Effet si Augmenté | Effet si Diminué |
|-----------|-----------------|-------------------|------------------|
| `epochs` | 2 | ⬆️ Meilleure performance (mais risque overfitting) | ⬇️ Plus rapide, moins bon |
| `learning_rate` | 2e-5 | ⚠️ Convergence instable | 🐌 Convergence lente |
| `batch_size` | 16 | 🚀 Plus rapide (mais plus de RAM) | 💾 Moins de RAM, plus lent |
| `improvement_threshold` | 0.02 (2%) | 🔒 Déploiement plus strict | ⚡ Déploiement plus fréquent |

---

## 🔐 Sécurité & Conformité

### **Anonymisation RGPD**

1. **Entités Détectées**
   - `PERSON` : Noms de personnes → `[PERSON_hash]`
   - `ORG` : Organisations → `[ORG_hash]`
   - `GPE` : Entités géopolitiques → `[GPE_hash]`
   - `LOC` : Lieux → `[LOC_hash]`

2. **Emails**
   - Détection : Regex `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`
   - Remplacement : `[EMAIL]`

3. **Hash SHA-256**
   - Algorithme : SHA-256
   - Taille : 8 premiers caractères
   - Exemple : `John Doe` → `a3f8d2e1`

### **Permissions IAM**

```yaml
Service Account: 24274638091-compute@developer.gserviceaccount.com

Rôles Requis:
  ✅ roles/storage.objectAdmin          # Lecture/écriture GCS
  ✅ roles/aiplatform.user              # Lancer pipelines Vertex AI
  ✅ roles/logging.logWriter            # Logs Cloud Logging
  ✅ roles/artifactregistry.reader      # Lire images containers
```

---

## 🚀 Guide de Déploiement

### **1. Setup Initial (Une seule fois)**

```bash
# 1. Installer dépendances locales
cd etape7-mlops
pip install -r requirements.txt

# 2. Authentification GCP
gcloud auth login
gcloud config set project digitalsocialscoreapi

# 3. Uploader les données vers GCS
python upload_data_to_gcs.py
# ✅ train.csv → gs://digitalsocialscoreapi_cloudbuild/data/train.csv
# ✅ test.csv  → gs://digitalsocialscoreapi_cloudbuild/data/test.csv
```

### **2. Lancement du Pipeline**

```bash
# 1. Compiler le pipeline (génère ml_pipeline_clean.json)
python clean_and_compile.py
# ✅ Pipeline compilé: vertex_pipelines/ml_pipeline_clean.json (26 KB)

# 2. Lancer sur Vertex AI (depuis Cloud Shell ou avec ADC)
python launch_pipeline_clean.py
# ✅ Pipeline job créé: digital-social-score-ml-pipeline-YYYYMMDDHHMMSS
```

### **3. Monitoring de l'Exécution**

```bash
# Option 1: Console Web
https://console.cloud.google.com/vertex-ai/pipelines/runs?project=digitalsocialscoreapi

# Option 2: CLI
gcloud ai pipeline-jobs list \
  --region=europe-west1 \
  --project=digitalsocialscoreapi

# Option 3: Logs
gcloud logging read \
  "resource.type=ml_job" \
  --limit=50 \
  --format=json
```

### **4. Vérification des Résultats**

```bash
# Lister les artefacts générés
gsutil ls -lhr gs://digitalsocialscoreapi_cloudbuild/vertex-pipelines/

# Télécharger le rapport d'évaluation
gsutil cp gs://digitalsocialscoreapi_cloudbuild/vertex-pipelines/.../evaluation_report.json .

# Voir la décision de déploiement
cat evaluation_report.json | jq '.should_deploy'
```

---

## 📈 Métriques de Succès

### **Métriques Techniques**

| Métrique | Objectif | Importance |
|----------|----------|------------|
| **F1-Score** | ≥ 0.85 | 🔴 Critique (décision de déploiement) |
| **Accuracy** | ≥ 0.90 | 🟡 Important |
| **Precision** | ≥ 0.85 | 🟢 Souhaitable (minimiser faux positifs) |
| **Recall** | ≥ 0.80 | 🟢 Souhaitable (minimiser faux négatifs) |

### **Métriques Opérationnelles**

| Métrique | Objectif | Mesure |
|----------|----------|--------|
| **Pipeline Success Rate** | ≥ 95% | % exécutions sans erreur |
| **Pipeline Duration** | ≤ 60 min | Temps total d'exécution |
| **Cost per Run** | ≤ $5 | Coût GCP par exécution |
| **Model Improvement Rate** | ≥ 30% | % de runs qui déploient |

---

## 🐛 Debugging & Troubleshooting

### **Problème 1: Pipeline Failed - prepare-data-op**

**Symptômes:**
```
Error: The replica workerpool0-0 exited with a non-zero status of 1
```

**Causes Possibles:**
1. ❌ spaCy model download échoue (connexion internet)
2. ❌ Données GCS inaccessibles (permissions)
3. ❌ Out of Memory (dataset trop gros)

**Solutions:**
```python
# 1. Vérifier que spaCy télécharge bien le modèle
os.system("python -m spacy download en_core_web_sm")
# → Regarder les logs pour "✔ Download and installation successful"

# 2. Vérifier permissions GCS
gsutil ls gs://digitalsocialscoreapi_cloudbuild/data/
# → Doit lister train.csv et test.csv

# 3. Augmenter timeout ou réduire dataset
# Dans @component decorator:
@component(
    base_image="python:3.10-slim",
    timeout="3600s"  # 1 heure au lieu de 20 min
)
```

### **Problème 2: Out of Memory (OOM)**

**Symptômes:**
```
Error: Container killed due to memory limit exceeded
```

**Solutions:**
```python
# 1. Réduire batch_size
batch_size = 8  # Au lieu de 16

# 2. Augmenter machine type (dans launch_pipeline_clean.py)
# Changer de e2-standard-4 (16 GB) à e2-standard-8 (32 GB)

# 3. Traiter les données par chunks
for chunk in pd.read_csv('/tmp/raw_data.csv', chunksize=10000):
    process_chunk(chunk)
```

### **Problème 3: Unicode Encoding Errors**

**Symptômes:**
```
UnicodeEncodeError: 'ascii' codec can't encode character
```

**Solution:**
```bash
# clean_and_compile.py gère déjà ça automatiquement
python clean_and_compile.py
# → Supprime tous les emojis et accents
```

---

## 📚 Ressources & Documentation

### **Documentation Officielle**
- [Vertex AI Pipelines](https://cloud.google.com/vertex-ai/docs/pipelines)
- [Kubeflow Pipelines SDK](https://kubeflow-pipelines.readthedocs.io/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [spaCy NER](https://spacy.io/usage/linguistic-features#named-entities)

### **Exemples & Tutoriels**
- [Vertex AI Pipeline Samples](https://github.com/GoogleCloudPlatform/vertex-ai-samples)
- [BERT Fine-tuning Tutorial](https://huggingface.co/docs/transformers/training)

### **Support**
- **Issues GitHub** : [Derrick-75/digital-social-score/issues](https://github.com/Derrick-75/digital-social-score/issues)
- **Documentation Interne** : `etape7-mlops/README.md`

---

## ✅ Checklist de Production

### **Avant le Premier Lancement**
- [x] Données uploadées sur GCS (train.csv, test.csv)
- [x] Service account configuré avec bonnes permissions
- [x] Pipeline compilé (`ml_pipeline_clean.json`)
- [ ] Tests unitaires des composants passés
- [ ] Exécution pipeline de bout en bout réussie

### **Avant la Mise en Production**
- [ ] Modèle déployé avec F1 ≥ 0.85
- [ ] API FastAPI déployée sur GKE
- [ ] Monitoring Prometheus configuré
- [ ] Alertes CloudWatch/Prometheus configurées
- [ ] Documentation à jour
- [ ] Runbook d'incident créé

### **Maintenance Continue**
- [ ] Réentraînement hebdomadaire automatisé (Cloud Scheduler)
- [ ] Dashboard de monitoring créé (Grafana)
- [ ] Logs centralisés (Cloud Logging)
- [ ] Backups GCS configurés
- [ ] Plan de disaster recovery testé

---

**Version:** 1.0.0  
**Date:** 9 novembre 2025  
**Auteurs:** Digital Social Score Team  
**Contact:** [GitHub Issues](https://github.com/Derrick-75/digital-social-score/issues)
