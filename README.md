# 🎯 Digital Social Score - API de Détection de Toxicité

> Projet TP ESIGELEC - De l'analyse de texte à l'infrastructure Cloud sécurisée, scalable et conforme

## 📋 Objectif

Concevoir et déployer une API qui :
- ✅ Détecte la toxicité d'un texte (injures, racisme, harcèlement, propos haineux)
- ✅ Attribue un score numérique de 0 à 100
- ✅ Respecte le RGPD (aucune donnée personnelle stockée en clair)
- ✅ Est scalable (passage de quelques utilisateurs à des milliers)
- ✅ Est observable et auditable (logs, métriques, alertes)
- ✅ Est documentée avec architecture Cloud justifiée

## 👥 Équipe

- **Membre 1** : [Nom] - Focus Data/IA
- **Membre 2** : [Nom] - Focus Infra/Cloud

## 📁 Structure du Projet

```
digital-social-score/
├── docs/                           # Documentation générale
│   ├── architecture-cloud.md       # Schéma et explications infrastructure
│   ├── registre-rgpd.md           # Registre de traitement des données
│   └── rapport-charge.md          # Résultats tests de charge
│
├── etape1-anonymisation/          # Étape 1 : RGPD & Anonymisation
│   ├── notebooks/                 # Jupyter notebooks d'exploration
│   ├── scripts/                   # Scripts d'anonymisation
│   └── data/                      # Données (gitignore)
│
├── etape2-modele-ia/              # Étape 2 : Entraînement modèles
│   ├── models/                    # Modèles sauvegardés
│   ├── training/                  # Scripts d'entraînement
│   ├── evaluation/                # Métriques et comparaisons
│   └── notebooks/                 # Expérimentations
│
├── etape3-api/                    # Étape 3 : API REST
│   ├── app/                       # Code FastAPI/Flask
│   ├── tests/                     # Tests unitaires
│   └── requirements.txt
│
├── etape4-securite/               # Étape 4 : Sécurité & RGPD
│   ├── config/                    # JWT, HTTPS, IAM
│   └── scripts/                   # Scripts de configuration
│
├── etape5-load-testing/           # Étape 5 : Tests de charge
│   ├── scripts/                   # Locust, k6, Apache Bench
│   └── results/                   # Résultats des tests
│
├── etape6-supervision/            # Étape 6 : Monitoring
│   ├── config/                    # Prometheus, Grafana
│   └── dashboards/                # Dashboards exportés
│
└── etape7-infrastructure/         # Étape 7 : Architecture Cloud
    └── diagrams/                  # Schémas d'architecture
```

## 🚀 Étapes du Projet

### Étape 1 : Exploration & Anonymisation des Données
- [ ] Télécharger dataset (Toxic Comment ou GameTox)
- [ ] Implémenter NER avec spaCy
- [ ] Comparer versions initiale et anonymisée
- [ ] Documenter registre RGPD

### Étape 2 : Préparation & Entraînement Modèle IA
- [ ] Nettoyage des textes
- [ ] Entraîner modèle statistique
- [ ] Entraîner modèle avancé (LSTM/BERT)
- [ ] Comparer performances

### Étape 3 : Déploiement API Cloud
- [ ] Exporter le modèle
- [ ] Créer API avec FastAPI/Flask
- [ ] Déployer sur Cloud (Vertex AI / AWS / Scaleway)
- [ ] Tester requêtes

### Étape 4 : Sécurisation & Conformité RGPD
- [ ] Configurer authentification (JWT / API Key)
- [ ] Mettre en place HTTPS
- [ ] Configurer IAM
- [ ] Finaliser registre RGPD

### Étape 5 : Simulation Montée en Charge
- [ ] Tests progressifs avec Locust/k6
- [ ] Stress tests
- [ ] Mesurer latence (P95/P99)
- [ ] Proposer améliorations

### Étape 6 : Sécurité & Supervision
- [ ] Configurer Prometheus/Grafana
- [ ] Analyser logs et anomalies
- [ ] Simuler pannes/attaques
- [ ] Évaluer continuité service

### Étape 7 : Modélisation Infrastructure Cloud
- [ ] Lister composants (API, IA, stockage, supervision)
- [ ] Dessiner flux et authentifications
- [ ] Schématiser architecture complète
- [ ] Rédiger documentation explicative

## 📦 Technologies Utilisées

### Data & IA
- Python 3.9+
- spaCy (NER)
- HuggingFace Transformers (BERT)
- TensorFlow/PyTorch (LSTM)
- Pandas, NumPy

### API & Backend
- FastAPI ou Flask
- Uvicorn
- Pydantic

### Cloud & Infrastructure
- AWS / GCP / Scaleway
- Docker
- Kubernetes (optionnel)

### Sécurité
- JWT
- HTTPS/TLS
- IAM

### Tests & Monitoring
- Locust / k6 / Apache Bench
- Prometheus
- Grafana
- pytest

## 📊 Livrables

1. ✅ API fonctionnelle et documentée
2. ✅ Exemples de requêtes/réponses
3. ✅ Schéma d'architecture Cloud + texte explicatif
4. ✅ Registre RGPD conforme
5. ✅ Tableau de bord supervision (captures)
6. ✅ Rapport simulation de charge
7. ✅ Grille tests sécurité/stress/failover

## 🎯 Critères d'Évaluation

| Compétence | Indicateurs |
|------------|-------------|
| **Fonctionnalité** | API opérationnelle, scoring correct |
| **Sécurité** | Authentification, validation, chiffrement |
| **Scalabilité** | Test de charge et analyse pertinente |
| **Supervision** | Logs/métriques, dashboard |
| **Conformité RGPD** | Anonymisation, registre conforme |
| **Présentation** | Documentation claire, schéma lisible, code commenté |

## 🚦 Getting Started

### 1. Cloner le repo
```bash
git clone https://github.com/[votre-username]/digital-social-score.git
cd digital-social-score
```

### 2. Installer les dépendances
```bash
# Pour chaque étape
cd etape3-api
pip install -r requirements.txt
```

### 3. Lancer l'API (après développement)
```bash
cd etape3-api
uvicorn app.main:app --reload
```

## 📚 Ressources

- [Toxic Comment Dataset](https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge)
- [GameTox Dataset](https://github.com/hwang-su/gametox)
- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [spaCy NER](https://spacy.io/usage/linguistic-features#named-entities)
- [CNIL - RGPD](https://www.cnil.fr/)

## 📝 Conventions de Code

- Code en **anglais** (variables, fonctions, commentaires)
- Documentation en **français**
- Format : **Black** (Python)
- Commits : messages clairs et descriptifs

## 📅 Timeline

| Semaine | Étapes |
|---------|--------|
| S1 | Étapes 1-2 |
| S2 | Étapes 3-4 |
| S3 | Étapes 5-6 |
| S4 | Étape 7 + Finalisations |

---

**Date de début** : [À compléter]  
**Date de rendu** : [À compléter]
