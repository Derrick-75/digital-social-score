# ✅ Checklist de vérification MLOps

## 📋 Structure des fichiers

### Racine etape7-mlops/
- [x] `requirements.txt` - Dépendances Python
- [x] `README.md` - Documentation principale
- [x] `QUICK_START.md` - Guide de démarrage rapide
- [x] `QUICKSTART.md` - Variante du guide
- [x] `compile_pipeline.py` - Script de compilation
- [x] `trigger_pipeline.py` - Script de déclenchement
- [x] `upload_data_to_gcs.py` - Upload des données
- [x] `test_setup.py` - Tests de validation
- [x] `setup-mlops.ps1` - Configuration GCP (PowerShell)
- [x] `run_mlops_pipeline.sh` - Script de lancement (Bash)
- [x] `.gitignore` - Configuration Git

### vertex_pipelines/
- [x] `__init__.py` - Module Python
- [x] `pipeline_definition.py` - Définition du pipeline
- [x] `trigger_pipeline.py` - Déclencheur alternatif

### vertex_pipelines/components/
- [x] `__init__.py` - Module Python
- [x] `prepare_data.py` - Composant de préparation
- [x] `train_model.py` - Composant d'entraînement
- [x] `evaluate_model.py` - Composant d'évaluation

---

## 🔍 Vérifications techniques

### 1. Dépendances Python
```bash
cd etape7-mlops
pip install -r requirements.txt
```

**Packages requis :**
- google-cloud-aiplatform==1.38.0
- kfp==2.4.0
- pandas, numpy, scikit-learn
- transformers, torch (pour BERT)
- google-cloud-storage

### 2. Configuration GCP
```bash
# Activer les APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable storage-api.googleapis.com

# Authentification
gcloud auth application-default login

# Créer le bucket
gsutil mb -p digitalsocialscoreapi -l europe-west1 gs://digitalsocialscoreapi-mlops/
```

### 3. Données d'entraînement
**Chemins requis :**
- `../etape1-anonymisation/data/raw/train_advanced.csv`
- `../etape1-anonymisation/data/raw/test_advanced.csv`

**Vérification :**
```bash
ls -lh ../etape1-anonymisation/data/raw/*.csv
```

### 4. Imports Python
**Test des imports :**
```python
import kfp
from google.cloud import aiplatform
import pandas as pd
import sklearn
```

---

## 🧪 Tests de validation

### Lancer les tests automatiques
```bash
cd etape7-mlops
python test_setup.py
```

**Résultats attendus :**
- ✅ Imports : PASS
- ✅ Composants : PASS
- ✅ Pipeline : PASS
- ✅ Données : PASS
- ✅ GCP : PASS

---

## 🚀 Étapes de démarrage

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Authentifier GCP
```bash
gcloud auth application-default login
```

### 3. Uploader les données
```bash
python upload_data_to_gcs.py
```

### 4. Compiler le pipeline
```bash
python compile_pipeline.py
```

### 5. Lancer le pipeline
```bash
python trigger_pipeline.py
```

---

## ⚠️ Points d'attention

### Bucket GCS
- **Nom** : `digitalsocialscoreapi-mlops` ou `digitalsocialscoreapi_cloudbuild`
- **Région** : `europe-west1`
- **Structure** :
  ```
  gs://bucket-name/
  ├── data/
  │   ├── train.csv
  │   └── test.csv
  ├── models/
  └── vertex-pipelines/
  ```

### Quotas Vertex AI
- Vérifier les quotas dans la console GCP
- Région : `europe-west1`

### Coûts estimés
- **Entraînement Simple** : ~0.50€ / run
- **Entraînement BERT** : ~2-5€ / run (GPU)

---

## 🔧 Dépannage

### Erreur "kfp not found"
```bash
pip install kfp==2.4.0
```

### Erreur "Permission denied"
```bash
gcloud auth application-default login
```

### Erreur "Bucket not found"
```bash
gsutil mb -p digitalsocialscoreapi -l europe-west1 gs://digitalsocialscoreapi-mlops/
```

### Erreur "spaCy model not found"
```bash
python -m spacy download en_core_web_sm
```

---

## ✅ Statut actuel

**Fichiers :** ✅ Tous en place  
**Structure :** ✅ Conforme  
**APIs GCP :** ✅ Activées  
**Bucket GCS :** ✅ Créé  
**Dépendances :** ⏳ À installer  
**Authentification :** ⏳ À configurer  
**Données uploadées :** ⏳ À faire  
**Pipeline compilé :** ⏳ À faire  

---

**Prêt pour les tests !** 🚀
