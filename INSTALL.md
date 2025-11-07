# 🚀 Guide d'Installation - Digital Social Score

## 📋 Prérequis

- **Python 3.9+** (recommandé : 3.11)
- **pip** (gestionnaire de packages Python)
- **Git** (pour cloner le projet)
- **Minimum 8GB RAM** (pour les modèles BERT)
- **Espace disque** : 5GB (datasets + modèles)

## ⚡ Installation Rapide

### 1. Cloner le projet
```bash
git clone https://github.com/esigelec/digital-social-score.git
cd digital-social-score
```

### 2. Installation automatique (recommandée)
```bash
# Linux/Mac
make setup

# Windows (PowerShell)
pip install -e ".[dev]"
./install_spacy_models.bat
```

### 3. Vérification
```bash
make health-check
```

## 📦 Installation Manuelle

### 1. Environnement virtuel (recommandé)
```bash
# Créer l'environnement
python -m venv venv

# Activer (Linux/Mac)
source venv/bin/activate

# Activer (Windows)
venv\Scripts\activate
```

### 2. Installation des dépendances
```bash
# Installation de base
pip install -e .

# Ou installation complète pour développement
pip install -e ".[dev]"

# Ou installation de tout (dev + monitoring + cloud)
pip install -e ".[all]"
```

### 3. Modèles spaCy
```bash
# Modèles requis pour l'anonymisation
python -m spacy download en_core_web_lg    # Anglais
python -m spacy download fr_core_news_lg   # Français
python -m spacy download xx_ent_wiki_sm    # Multilingue
```

## 🎯 Installation par Composant

### API seulement
```bash
pip install fastapi uvicorn pydantic scikit-learn transformers torch
```

### Notebooks et IA
```bash
pip install pandas numpy matplotlib seaborn scikit-learn transformers torch spacy nltk jupyter
```

### Tests et développement
```bash
pip install pytest pytest-cov black isort flake8 mypy pre-commit
```

## 🐳 Installation avec Docker

### 1. Construction de l'image
```bash
cd etape3-api
docker build -t digital-social-score .
```

### 2. Lancement
```bash
docker run -p 8000:8000 digital-social-score
```

## 🔧 Configuration

### 1. Variables d'environnement
```bash
cp etape3-api/.env.example etape3-api/.env
# Éditer .env avec vos paramètres
```

### 2. Téléchargement des datasets
```bash
# Placer vos datasets dans :
# etape1-anonymisation/data/raw/
# - train_advanced.csv
# - test_advanced.csv
```

## ✅ Vérification de l'installation

### 1. Tests unitaires
```bash
make test
# ou
pytest etape3-api/tests/
```

### 2. API locale
```bash
make run-api
# Aller sur http://localhost:8000/docs
```

### 3. Notebooks
```bash
make run-notebooks
# Ou jupyter lab
```

## 🚨 Résolution de Problèmes

### Erreur : Module spaCy non trouvé
```bash
pip install spacy
python -m spacy download en_core_web_lg
```

### Erreur : PyTorch installation
```bash
# CPU seulement
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# GPU (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Erreur : Mémoire insuffisante
- Réduire la taille du batch dans les notebooks BERT
- Utiliser le modèle DistilBERT au lieu de BERT
- Augmenter la swap/mémoire virtuelle

### Erreur : Permissions Docker
```bash
# Linux : ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
# Redémarrer la session
```

## 📊 Structure des Dépendances

```
digital-social-score/
├── Core ML (obligatoire)
│   ├── pandas, numpy, scikit-learn
│   ├── torch, transformers
│   └── spacy, nltk
├── API (obligatoire pour étape 3)
│   ├── fastapi, uvicorn, pydantic
│   └── python-jose, passlib
├── Notebooks (optionnel)
│   ├── jupyter, matplotlib, seaborn
│   └── tqdm, ipywidgets
├── Dev/Test (optionnel)
│   ├── pytest, black, isort
│   └── mypy, flake8, pre-commit
└── Cloud/Monitoring (optionnel)
    ├── docker, boto3, google-cloud
    └── prometheus-client, locust
```

## 🎯 Commandes Utiles

```bash
# Vérifier les versions installées
pip list | grep -E "(pandas|fastapi|torch|transformers|spacy)"

# Voir l'espace utilisé
du -sh venv/  # Linux/Mac
dir venv      # Windows

# Mise à jour des dépendances
pip install --upgrade -e ".[dev]"

# Désinstallation complète
pip uninstall digital-social-score
rm -rf venv
```

## 📚 Prochaines Étapes

1. **Données** : Placer vos datasets dans `etape1-anonymisation/data/raw/`
2. **Anonymisation** : `make anonymize-data`
3. **Preprocessing** : Exécuter `etape2-modele-ia/notebooks/preprocessing.ipynb`
4. **Modèles** : `make train-model`
5. **API** : `make run-api`
6. **Tests** : `make test`

## 💬 Support

- **Issues** : [GitHub Issues](https://github.com/esigelec/digital-social-score/issues)
- **Documentation** : Voir les README de chaque étape
- **FAQ** : [docs/FAQ.md](docs/FAQ.md)

---
**Projet ESIGELEC - Digital Social Score v1.0**
