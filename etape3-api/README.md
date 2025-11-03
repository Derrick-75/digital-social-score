# Étape 3 : Déploiement du Modèle en API Cloud

## 🎯 Objectifs Pédagogiques

- Transformer le modèle IA en service accessible
- Utiliser FastAPI, Flask ou un service Cloud (Vertex AI, Scaleway, AWS)

## 📋 Exercices

### 1. Export du Modèle
- [ ] Sauvegarder le modèle entraîné
- [ ] Créer script de chargement optimisé
- [ ] Tester le chargement et l'inférence

### 2. Création de l'API
- [ ] Choisir framework : **FastAPI (recommandé)** ou Flask
- [ ] Créer endpoint POST `/analyze`
- [ ] Définir schéma de requête/réponse
- [ ] Implémenter la logique de scoring

### 3. Déploiement Cloud
- [ ] Containeriser avec Docker
- [ ] Déployer sur plateforme Cloud :
  - AWS (Lambda + API Gateway)
  - GCP (Cloud Run)
  - Scaleway
- [ ] Configurer domaine et HTTPS

### 4. Tests de l'API
- [ ] Tester avec curl/Postman
- [ ] Créer suite de tests (pytest)
- [ ] Documenter exemples de requêtes

## 🛠️ Technologies

```bash
pip install fastapi uvicorn pydantic transformers torch
```

## 📁 Structure

```
etape3-api/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Point d'entrée FastAPI
│   ├── models.py                  # Schémas Pydantic
│   ├── inference.py               # Logique d'inférence
│   └── config.py                  # Configuration
├── tests/
│   ├── test_api.py                # Tests unitaires
│   └── test_inference.py
├── Dockerfile                     # Image Docker
├── requirements.txt               # Dépendances Python
└── README.md
```

## 🚀 Architecture API

```
Client
  ↓ POST /analyze
API Gateway
  ↓
FastAPI App
  ↓
Model Inference
  ↓
Response (score + détails)
```

## 📝 Exemple de Requête/Réponse

### Requête POST `/analyze`
```json
{
  "text": "Ce commentaire est vraiment méchant et insultant"
}
```

### Réponse
```json
{
  "score": 87,
  "toxicity_level": "high",
  "categories": {
    "insult": 0.85,
    "threat": 0.12,
    "hate": 0.45
  },
  "processing_time_ms": 245
}
```

## 🐳 Dockerfile Exemple

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY models/ ./models/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## 📊 Livrables

- [ ] Code API complet et fonctionnel
- [ ] Documentation OpenAPI automatique (FastAPI)
- [ ] Dockerfile et image buildée
- [ ] API déployée et accessible (URL publique)
- [ ] Collection Postman avec exemples
- [ ] Tests unitaires (couverture > 80%)

## ✅ Critères de Validation

- ✅ API répond correctement aux requêtes
- ✅ Temps de réponse < 500ms
- ✅ Validation des entrées (Pydantic)
- ✅ Gestion des erreurs (404, 422, 500)
- ✅ Documentation interactive accessible
- ✅ Déployée sur Cloud avec HTTPS

## 💡 Bonnes Pratiques

### FastAPI Features à Utiliser
- **Validation automatique** avec Pydantic
- **Documentation auto** : `/docs` (Swagger UI)
- **Performance** : async/await
- **Type hints** : meilleure maintenabilité

### Optimisations
- **Cache du modèle** : charger une seule fois au startup
- **Batch processing** : traiter plusieurs textes ensemble
- **Rate limiting** : limiter les abus

### Monitoring
- Logs structurés (JSON)
- Temps de réponse par endpoint
- Erreurs HTTP

## 🌐 Options de Déploiement

| Plateforme | Avantages | Inconvénients |
|------------|-----------|---------------|
| **AWS Lambda** | Serverless, pay-per-use | Cold start, limite 15min |
| **GCP Cloud Run** | Simple, auto-scale | Coût si trafic élevé |
| **Scaleway** | Européen, RGPD-friendly | Moins de features |
| **Heroku** | Gratuit (hobby), simple | Limité en perfs |

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [AWS Lambda + FastAPI](https://mangum.io/)
