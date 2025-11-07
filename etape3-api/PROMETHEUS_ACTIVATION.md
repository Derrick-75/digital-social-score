# ✅ Prometheus Activé - Digital Social Score API

**Date** : 07/11/2025  
**Status** : ✅ Configuré et prêt pour le déploiement

---

## 📋 Résumé des Modifications

### ✅ **Fichiers Créés / Modifiés**

1. **`app/metrics.py`** - Module Prometheus ✅
   - Métriques custom : `toxicity_requests`, `toxicity_score`, `toxicity_processing_time`
   - Instrumentateur FastAPI pour métriques automatiques
   - Fonction `setup_metrics()` pour activer Prometheus

2. **`requirements.txt`** - Dépendances ajoutées ✅
   ```txt
   prometheus-client==0.19.0
   prometheus-fastapi-instrumentator==6.1.0
   ```

3. **`app/main.py`** - Intégration Prometheus ✅
   - Import des métriques
   - Activation automatique au démarrage
   - Enregistrement des métriques dans `/analyze`
   - Comptage des erreurs

---

## 📊 Métriques Exportées

### **Métriques Custom**

| Métrique | Type | Description |
|----------|------|-------------|
| `toxicity_api_requests_total` | Counter | Nombre total de requêtes d'analyse |
| `toxicity_score_distribution` | Histogram | Distribution des scores de toxicité (0-100) |
| `toxicity_processing_seconds` | Histogram | Temps de traitement en secondes |
| `toxicity_api_active_users` | Gauge | Nombre d'utilisateurs actifs |
| `model_load_seconds` | Histogram | Temps de chargement des modèles |

### **Métriques Automatiques (FastAPI Instrumentator)**

- `http_requests_total` - Nombre total de requêtes HTTP
- `http_request_duration_seconds` - Durée des requêtes HTTP
- `http_requests_inprogress` - Requêtes en cours de traitement
- `http_request_size_bytes` - Taille des requêtes
- `http_response_size_bytes` - Taille des réponses

---

## 🔗 Endpoint Prometheus

**URL** : `/metrics`

**Format** : Prometheus Text Format

**Exemple de sortie** :
```prometheus
# HELP toxicity_api_requests_total Nombre total de requêtes d'analyse de toxicité
# TYPE toxicity_api_requests_total counter
toxicity_api_requests_total{model_type="simple",status="success"} 42.0
toxicity_api_requests_total{model_type="bert",status="success"} 18.0

# HELP toxicity_score_distribution Distribution des scores de toxicité retournés
# TYPE toxicity_score_distribution histogram
toxicity_score_distribution_bucket{le="10.0"} 5.0
toxicity_score_distribution_bucket{le="50.0"} 32.0
toxicity_score_distribution_bucket{le="100.0"} 60.0
toxicity_score_distribution_sum 2450.5
toxicity_score_distribution_count 60.0

# HELP toxicity_processing_seconds Temps de traitement de l'analyse de toxicité
# TYPE toxicity_processing_seconds histogram
toxicity_processing_seconds_bucket{le="0.01",model_type="simple"} 15.0
toxicity_processing_seconds_bucket{le="0.1",model_type="simple"} 40.0
toxicity_processing_seconds_sum{model_type="simple"} 1.245
toxicity_processing_seconds_count{model_type="simple"} 42.0
```

---

## 🚀 Déploiement sur GCP

### **Option 1 : Google Managed Prometheus (Recommandé)**

1. **Annoter le Service Kubernetes**
   
   Modifiez `k8s/service.yaml` :
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: toxicity-api
     annotations:
       # Activer Google Managed Prometheus
       cloud.google.com/prometheus-scrape: "true"
       cloud.google.com/prometheus-scrape-port: "8000"
       cloud.google.com/prometheus-scrape-path: "/metrics"
   spec:
     selector:
       app: toxicity-api
     ports:
       - port: 80
         targetPort: 8000
   ```

2. **Redéployer sur GKE**
   ```powershell
   kubectl apply -f k8s/service.yaml
   kubectl apply -f k8s/deployment.yaml
   ```

3. **Vérifier la collecte des métriques**
   
   Allez sur :
   ```
   https://console.cloud.google.com/monitoring/metrics-explorer
   ```
   
   Recherchez les métriques commençant par `toxicity_api_`

4. **Créer un Dashboard**
   
   Les métriques Prometheus seront automatiquement disponibles dans Cloud Monitoring !

---

### **Option 2 : Exposer /metrics publiquement (Pour Tests)**

Si vous voulez tester `/metrics` depuis l'extérieur :

1. **Modifier le Ingress** (`k8s/ingress.yaml`) :
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: toxicity-api-ingress
   spec:
     rules:
     - http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: toxicity-api
               port:
                 number: 80
         - path: /metrics  # Ajouter cette route
           pathType: Exact
           backend:
             service:
               name: toxicity-api
               port:
                 number: 80
   ```

2. **Tester** :
   ```powershell
   curl http://34.38.214.124/metrics
   ```

⚠️ **Attention** : En production, sécurisez `/metrics` avec une authentification !

---

## 📊 Utilisation avec Cloud Monitoring

### **Requêtes MQL pour Dashboard**

**1. Nombre de requêtes par seconde** :
```sql
fetch prometheus_target
| metric 'prometheus.googleapis.com/toxicity_api_requests_total/counter'
| group_by 1m, [value_toxicity_api_requests_total_sum: sum(value.toxicity_api_requests_total)]
| every 1m
| group_by [resource.cluster, metric.model_type],
    [value_toxicity_api_requests_total_mean: mean(value_toxicity_api_requests_total_sum)]
```

**2. Latence P95** :
```sql
fetch prometheus_target
| metric 'prometheus.googleapis.com/toxicity_processing_seconds/histogram'
| group_by 1m, [value_toxicity_processing_seconds_95: percentile(value.toxicity_processing_seconds, 95)]
```

**3. Distribution des scores** :
```sql
fetch prometheus_target
| metric 'prometheus.googleapis.com/toxicity_score_distribution/histogram'
| group_by [metric.le], [value_sum: sum(value.toxicity_score_distribution)]
```

---

## 🧪 Tests Locaux

### **Démarrer l'API** :
```powershell
cd etape3-api
python -m uvicorn app.main:app --reload --port 8000
```

### **Tester /metrics** :
```powershell
curl http://localhost:8000/metrics
```

### **Envoyer des requêtes pour générer des métriques** :
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/analyze" -Method Post -ContentType "application/json" -Body '{"text": "Test", "model": "simple"}'
```

### **Vérifier les métriques** :
```powershell
curl http://localhost:8000/metrics | Select-String "toxicity"
```

---

## 🎯 Intégration avec Locust

Maintenant que Prometheus est activé, vos tests Locust génèreront automatiquement des métriques détaillées !

### **Pendant un test Locust** :

1. **Lancez Locust** :
   ```powershell
   cd ../etape5-load-testing
   .\run_tests.ps1
   ```

2. **Observez les métriques en temps réel** :
   - Cloud Monitoring Dashboard
   - Ou `/metrics` endpoint

3. **Analysez après le test** :
   - Corrélation entre charge Locust et métriques serveur
   - Identification des goulots d'étranglement

---

## ✅ Checklist de Déploiement

- [x] Dépendances Prometheus installées
- [x] Module `metrics.py` créé
- [x] Intégration dans `main.py`
- [x] Métriques enregistrées dans `/analyze`
- [ ] Annotations K8s pour Google Managed Prometheus
- [ ] Redéploiement sur GKE
- [ ] Vérification de la collecte dans Cloud Monitoring
- [ ] Création du dashboard Cloud Monitoring
- [ ] Tests avec Locust + métriques Prometheus

---

## 📚 Ressources

- [Prometheus Client Python](https://github.com/prometheus/client_python)
- [FastAPI Instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator)
- [Google Managed Prometheus](https://cloud.google.com/stackdriver/docs/managed-prometheus)

---

**Status** : ✅ Prêt pour le déploiement sur GCP avec monitoring Prometheus complet !
