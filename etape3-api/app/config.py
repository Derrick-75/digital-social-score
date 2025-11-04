"""
Configuration de l'API Digital Social Score
"""
import os
from pathlib import Path

# Chemins des modèles
BASE_DIR = Path(__file__).parent.parent
MODEL_DIR = BASE_DIR / "models"
BERT_MODEL_PATH = BASE_DIR.parent / "etape2-modele-ia" / "models" / "bert_model"
SIMPLE_MODEL_PATH = BASE_DIR.parent / "etape2-modele-ia" / "models" / "simple_model"

# Configuration API
API_TITLE = "Digital Social Score API"
API_DESCRIPTION = """
🛡️ **API de Détection de Toxicité - Conforme RGPD**

Cette API utilise des modèles d'IA avancés pour détecter et scorer la toxicité dans les textes.

## Fonctionnalités

* **Analyse de toxicité** avec modèle BERT fine-tuné
* **Score de 0 à 100** (plus élevé = plus toxique)
* **Catégorisation** des types de toxicité
* **Temps de réponse optimisé** (< 500ms)
* **Conformité RGPD** (aucune donnée stockée)

## Utilisation

Envoyez une requête POST à `/analyze` avec votre texte pour obtenir un score de toxicité.
"""
API_VERSION = "1.0.0"

# Paramètres de l'IA
MAX_TEXT_LENGTH = 5000
DEFAULT_MODEL = "bert"  # "bert" ou "simple"
INFERENCE_TIMEOUT = 30  # secondes

# Rate limiting (requêtes par minute)
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60

# Configuration CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "https://digital-social-score.app"
]

# Niveaux de toxicité
TOXICITY_LEVELS = {
    "low": (0, 25),
    "medium": (25, 60),
    "high": (60, 85),
    "extreme": (85, 100)
}

# Configuration de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
