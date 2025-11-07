# Makefile pour le projet Digital Social Score
.PHONY: install install-dev install-models clean test lint format run-api build-docker help

# Variables
PYTHON := python
PIP := pip
PROJECT_NAME := digital-social-score

# Installation de base
install:
	@echo "📦 Installation des dépendances de base..."
	$(PIP) install -e .

# Installation pour développement
install-dev:
	@echo "🛠️ Installation pour développement..."
	$(PIP) install -e ".[dev]"
	pre-commit install

# Installation complète (toutes les dépendances optionnelles)
install-all:
	@echo "🔧 Installation complète..."
	$(PIP) install -e ".[all]"

# Installation des modèles spaCy
install-models:
	@echo "🚀 Installation des modèles spaCy..."
	@if [ "$(OS)" = "Windows_NT" ]; then \
		./install_spacy_models.bat; \
	else \
		bash install_spacy_models.sh; \
	fi

# Setup complet du projet
setup: install-dev install-models
	@echo "✅ Setup complet terminé !"

# Nettoyage
clean:
	@echo "🧹 Nettoyage des fichiers temporaires..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +

# Tests
test:
	@echo "🧪 Exécution des tests..."
	pytest

test-coverage:
	@echo "📊 Tests avec coverage..."
	pytest --cov --cov-report=html --cov-report=term

# Linting et formatage
lint:
	@echo "🔍 Vérification du code..."
	flake8 etape3-api/app
	mypy etape3-api/app

format:
	@echo "✨ Formatage du code..."
	black etape3-api/app etape1-anonymisation/scripts etape2-modele-ia
	isort etape3-api/app etape1-anonymisation/scripts etape2-modele-ia

# Exécution des services
run-api:
	@echo "🚀 Démarrage de l'API..."
	cd etape3-api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-notebooks:
	@echo "📓 Démarrage Jupyter..."
	jupyter lab

# Données et modèles
anonymize-data:
	@echo "🛡️ Anonymisation des données..."
	cd etape1-anonymisation && python scripts/anonymize.py

train-model:
	@echo "🤖 Entraînement du modèle..."
	cd etape2-modele-ia && python quick_train_model.py

preprocess-data:
	@echo "🧹 Préprocessing des données..."
	cd etape2-modele-ia/notebooks && jupyter nbconvert --execute preprocessing.ipynb

# Docker
build-docker:
	@echo "🐳 Construction de l'image Docker..."
	cd etape3-api && docker build -t $(PROJECT_NAME):latest .

run-docker:
	@echo "🐳 Démarrage du conteneur Docker..."
	docker run -p 8000:8000 $(PROJECT_NAME):latest

# Tests de charge
load-test:
	@echo "⚡ Tests de charge avec Locust..."
	cd etape5-load-testing && locust -f scripts/locustfile.py

# Documentation
docs:
	@echo "📚 Génération de la documentation..."
	@echo "Voir http://localhost:8000/docs pour la doc API"

# Vérification de santé du projet
health-check:
	@echo "🏥 Vérification de santé du projet..."
	@echo "Python version:" && $(PYTHON) --version
	@echo "Packages installés:" && $(PIP) list | grep -E "(pandas|fastapi|torch|transformers|spacy)"
	@echo "Modèles spaCy:" && $(PYTHON) -m spacy info | head -10

# Aide
help:
	@echo "🎯 Digital Social Score - Commandes Makefile"
	@echo ""
	@echo "Installation:"
	@echo "  install       - Installation de base"
	@echo "  install-dev   - Installation pour développement"
	@echo "  install-all   - Installation complète"
	@echo "  install-models- Installation modèles spaCy"
	@echo "  setup         - Setup complet du projet"
	@echo ""
	@echo "Développement:"
	@echo "  test          - Exécuter les tests"
	@echo "  test-coverage - Tests avec coverage"
	@echo "  lint          - Vérification du code"
	@echo "  format        - Formatage du code"
	@echo "  clean         - Nettoyage"
	@echo ""
	@echo "Exécution:"
	@echo "  run-api       - Démarrer l'API"
	@echo "  run-notebooks - Démarrer Jupyter"
	@echo "  run-docker    - Démarrer avec Docker"
	@echo ""
	@echo "Données & IA:"
	@echo "  anonymize-data - Anonymiser les données"
	@echo "  preprocess-data- Préprocesser les données"
	@echo "  train-model   - Entraîner le modèle"
	@echo ""
	@echo "Docker:"
	@echo "  build-docker  - Construire l'image"
	@echo ""
	@echo "Tests:"
	@echo "  load-test     - Tests de charge"
	@echo ""
	@echo "Utilitaires:"
	@echo "  health-check  - Vérification système"
	@echo "  docs          - Documentation"
	@echo "  help          - Cette aide"
