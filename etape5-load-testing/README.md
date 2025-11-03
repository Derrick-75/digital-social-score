# Étape 5 : Simulation de Montée en Charge

## Objectifs Pédagogiques

- Expérimenter la différence entre un prototype et un service scalable
- Utiliser Apache Bench, Locust ou k6 pour tester la charge
- Analyser les métriques de performance

## Exercices

### 1. Tests Progressifs
- [ ] Test baseline : 10 utilisateurs, 1 minute
- [ ] Test croissance : 50, 100, 200, 500 utilisateurs
- [ ] Identifier le point de rupture

### 2. Stress Test
- [ ] Saturer le système volontairement
- [ ] Observer les comportements en limite
- [ ] Mesurer temps de récupération

### 3. Failover Test
- [ ] Simuler panne d'un composant
- [ ] Vérifier basculement automatique (si HA)
- [ ] Mesurer impact utilisateur

### 4. Analyse des Résultats
- [ ] Calculer métriques clés :
  - Latence moyenne
  - Latence P95/P99
  - Taux d'erreur
  - Throughput (req/sec)
- [ ] Identifier goulots d'étranglement
- [ ] Proposer améliorations

## Technologies

### Outils de Test de Charge

#### 1. Apache Bench (Simple, rapide)
```bash
# Installation
sudo apt-get install apache2-utils

# Test basique
ab -n 1000 -c 10 https://localhost:8000/analyze \
   -p data.json \
   -T "application/json" \
   -H "Authorization: Bearer TOKEN"
```

#### 2. Locust (Recommandé - Python)
```bash
# Installation
pip install locust --break-system-packages

# Lancement
locust -f scripts/locustfile.py --host=https://localhost:8000
```

#### 3. k6 (Moderne - JavaScript)
```bash
# Installation (Linux)
wget https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz
tar -xzf k6-v0.47.0-linux-amd64.tar.gz
sudo mv k6-v0.47.0-linux-amd64/k6 /usr/local/bin/

# Test
k6 run scripts/load-test.js
```

## Structure

```
etape5-load-testing/
├── scripts/
│   ├── locustfile.py              # Script Locust
│   ├── load-test.js               # Script k6
│   ├── ab-test.sh                 # Script Apache Bench
│   └── analyze-results.py         # Analyse automatique
└── results/
    ├── baseline-10users.csv       # Résultats tests
    ├── stress-500users.csv
    ├── graphs/                    # Graphiques générés
    └── report.md                  # Rapport d'analyse
```

## Livrables

- [ ] Scripts de tests pour 3 scénarios minimum
- [ ] Résultats bruts (CSV/JSON)
- [ ] Graphiques de performance
- [ ] Rapport d'analyse avec :
  - Métriques clés
  - Identification bottlenecks
  - Recommandations d'amélioration
- [ ] Preuve de point de rupture
- [ ] Plan d'optimisation

## Critères de Validation

- ✅ Au moins 3 scénarios de charge testés
- ✅ Latence P95 < 500ms (objectif)
- ✅ Taux d'erreur < 1% (objectif)
- ✅ Point de rupture identifié et documenté
- ✅ Recommandations concrètes et chiffrées

## Exemple : Script Locust

```python
# scripts/locustfile.py
from locust import HttpUser, task, between
import json

class ToxicityUser(HttpUser):
    wait_time = between(1, 3)  # Attente entre requêtes
    
    def on_start(self):
        # Authentification
        response = self.client.post("/token", 
            data={"username": "test", "password": "test"})
        self.token = response.json()["access_token"]
    
    @task(3)  # Poids 3
    def analyze_normal_text(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {"text": "Ceci est un commentaire normal"}
        self.client.post("/analyze", 
            headers=headers, 
            json=payload, 
            name="/analyze [normal]")
    
    @task(1)  # Poids 1
    def analyze_toxic_text(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {"text": "Message avec insultes"}
        self.client.post("/analyze", 
            headers=headers, 
            json=payload, 
            name="/analyze [toxic]")
```

Lancement :
```bash
locust -f scripts/locustfile.py \
       --host=https://localhost:8000 \
       --users 100 \
       --spawn-rate 10 \
       --run-time 5m \
       --html=results/report.html
```

## Exemple : Script k6

```javascript
// scripts/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 10 },   // Montée à 10 users
    { duration: '2m', target: 50 },   // Montée à 50 users
    { duration: '2m', target: 50 },   // Maintien
    { duration: '1m', target: 100 },  // Spike à 100
    { duration: '2m', target: 0 },    // Descente
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% sous 500ms
    http_req_failed: ['rate<0.01'],    // <1% erreurs
  },
};

export default function () {
  const url = 'https://localhost:8000/analyze';
  const payload = JSON.stringify({
    text: 'Test de charge sur le système',
  });
  
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer YOUR_TOKEN',
    },
  };

  let response = http.post(url, payload, params);
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

## Métriques à Analyser

### 1. Latence
```
- Moyenne : Temps moyen de réponse
- Médiane (P50) : 50% des requêtes sous ce temps
- P95 : 95% des requêtes sous ce temps
- P99 : 99% des requêtes sous ce temps
- Max : Pire cas
```

**Objectifs** :
- Moyenne < 200ms
- P95 < 500ms
- P99 < 1000ms

### 2. Throughput
```
- Requêtes/seconde (RPS)
- Données transférées/sec (MB/s)
```

**Objectif** : > 100 RPS

### 3. Taux d'Erreur
```
- % de requêtes échouées
- Types d'erreurs (4xx, 5xx)
```

**Objectif** : < 1%

### 4. Ressources Système
```
- CPU utilization
- RAM usage
- Network I/O
- Disk I/O
```

## Améliorations Proposées

Basé sur les résultats, implémenter :

### 1. Cache
```python
# Redis pour cache des réponses fréquentes
import redis

cache = redis.Redis(host='localhost', port=6379)

def get_toxicity_score(text):
    cache_key = f"toxicity:{hash(text)}"
    cached = cache.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    score = model.predict(text)
    cache.setex(cache_key, 3600, json.dumps(score))  # 1h TTL
    return score
```

### 2. Load Balancer
```yaml
# nginx.conf
upstream api_backend {
    least_conn;
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://api_backend;
    }
}
```

### 3. Autoscaling (Kubernetes)
```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Template Rapport

```markdown
# Rapport de Tests de Charge - Digital Social Score

## Résumé Exécutif
- Point de rupture : XXX utilisateurs concurrents
- Latence P95 : XXX ms
- Taux d'erreur maximal : X.X%
- Recommandation : [Mise en prod OK / Optimisations nécessaires]

## Méthodologie
- Outil : Locust / k6
- Durée : X minutes
- Scénarios testés : X

## Résultats Détaillés

### Scénario 1 : Baseline (10 users)
- Latence moyenne : XXX ms
- P95 : XXX ms
- Throughput : XXX req/s
- Taux erreur : X%

[Graphique]

### Scénario 2 : Normal Load (50 users)
[...]

### Scénario 3 : Stress (500 users)
[...]

## Analyse
### Bottlenecks Identifiés
1. [CPU saturé à 95%]
2. [Temps inférence modèle trop long]
3. [...]

### Points Forts
1. [Taux d'erreur stable]
2. [...]

## Recommandations
1. **Court terme** : [Cache Redis]
2. **Moyen terme** : [Load balancer]
3. **Long terme** : [Kubernetes + autoscaling]

## Annexes
- Graphiques détaillés
- Logs d'erreurs
- Configuration système
```

## Ressources

- [Locust Documentation](https://docs.locust.io/)
- [k6 Documentation](https://k6.io/docs/)
- [Apache Bench Guide](https://httpd.apache.org/docs/2.4/programs/ab.html)
- [Performance Testing Best Practices](https://k6.io/docs/testing-guides/test-types/)
