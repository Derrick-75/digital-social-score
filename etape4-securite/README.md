# Étape 4 : Sécurisation et Conformité RGPD

## Objectifs Pédagogiques

- Mettre en place authentification et chiffrement
- Garantir la conformité RGPD (validation, logs pseudonymes)

## Exercices

### 1. Authentification et Autorisation
- [ ] Choisir méthode : **JWT** (recommandé) ou API Key
- [ ] Implémenter l'authentification
- [ ] Tester avec différents scénarios (valide, invalide, expiré)

### 2. Chiffrement et Sécurité Transport
- [ ] Configurer HTTPS/TLS
- [ ] Générer certificats (Let's Encrypt ou self-signed pour dev)
- [ ] Forcer redirection HTTP → HTTPS

### 3. IAM (Identity and Access Management)
- [ ] Définir rôles et permissions :
  - Admin : accès complet
  - User : accès API uniquement
  - Monitoring : lecture logs uniquement
- [ ] Implémenter système de rôles

### 4. Finalisation Registre RGPD
- [ ] Compléter `docs/registre-rgpd.md`
- [ ] Documenter :
  - Durées de conservation
  - Procédures de suppression
  - Droits des utilisateurs
  - Mesures de sécurité

## Technologies

```bash
# Authentification JWT
pip install pyjwt python-jose --break-system-packages

# Chiffrement
pip install cryptography --break-system-packages

# Environnement variables (secrets)
pip install python-dotenv --break-system-packages
```

## Structure

```
etape4-securite/
├── config/
│   ├── jwt_config.py              # Configuration JWT
│   ├── iam_roles.py               # Définition des rôles
│   └── https_config.py            # Config SSL/TLS
└── scripts/
    ├── generate_keys.py           # Génération clés JWT
    ├── setup_iam.py               # Setup IAM
    └── test_security.py           # Tests de sécurité
```

## Livrables

- [ ] Authentification JWT fonctionnelle
- [ ] HTTPS activé
- [ ] IAM configuré avec au moins 2 rôles
- [ ] Registre RGPD finalisé
- [ ] Documentation des endpoints sécurisés
- [ ] Tests de sécurité (attaques simples)

## Critères de Validation

- ✅ Impossible d'accéder à l'API sans token valide
- ✅ Token expiré rejeté automatiquement
- ✅ HTTPS obligatoire (HTTP refusé)
- ✅ Logs d'audit générés pour accès sensibles
- ✅ Secrets jamais en clair dans le code

## Bonnes Pratiques

### Gestion des Secrets
```python
# ❌ MAL
SECRET_KEY = "ma-cle-secrete-123"

# ✅ BIEN
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
```

### JWT Best Practices
- Expiration courte (15-60 minutes)
- Refresh token pour renouvellement
- Algorithme HS256 ou RS256
- Claims minimal (pas de données sensibles)

### IAM
- Principe du moindre privilège
- Séparation des responsabilités
- Audit régulier des accès

## Ressources

- [JWT.io](https://jwt.io/) - Débugger JWT
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [CNIL - Sécurité](https://www.cnil.fr/fr/securite)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

## Tests de Sécurité

### Test 1 : Sans Authentification
```bash
curl -X POST https://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Test"}'

# Attendu : 401 Unauthorized
```

### Test 2 : Token Invalide
```bash
curl -X POST https://localhost:8000/analyze \
  -H "Authorization: Bearer FAKE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test"}'

# Attendu : 401 ou 403
```

### Test 3 : Token Valide
```bash
# 1. Obtenir token
TOKEN=$(curl -X POST https://localhost:8000/token \
  -d "username=user&password=pass" | jq -r '.access_token')

# 2. Utiliser token
curl -X POST https://localhost:8000/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test"}'

# Attendu : 200 OK avec réponse
```

## Checklist RGPD

- [ ] Données pseudonymisées/anonymisées
- [ ] Chiffrement en transit (HTTPS)
- [ ] Chiffrement au repos (si stockage)
- [ ] Durées de conservation définies
- [ ] Procédure de suppression documentée
- [ ] Logs d'audit activés
- [ ] Registre de traitement complété
- [ ] Information des utilisateurs (CGU/politique)
- [ ] Consentement explicite (si applicable)
- [ ] Droits utilisateurs implémentés (accès, suppression)
