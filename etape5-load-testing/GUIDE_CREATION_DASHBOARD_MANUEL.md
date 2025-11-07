# 📊 Guide: Créer le Dashboard Cloud Monitoring Manuellement

## ✅ Statut des Métriques

Les métriques Prometheus sont **activées et fonctionnelles** :
- ✅ **127 requêtes traitées** depuis le pod
- ✅ **Score moyen: 48.3**
- ✅ **Distribution des scores** : majoritairement entre 40-50
- ✅ **PodMonitoring** configuré et actif

## 🎯 Création du Dashboard (Méthode Manuelle)

### Étape 1: Accéder à Cloud Monitoring

Ouvrez l'une de ces URLs :

**Metrics Explorer** (pour vérifier les métriques) :
```
https://console.cloud.google.com/monitoring/metrics-explorer?project=digitalsocialscoreapi
```

**Dashboards** (pour créer le dashboard) :
```
https://console.cloud.google.com/monitoring/dashboards?project=digitalsocialscoreapi
```

### Étape 2: Créer un Nouveau Dashboard

1. Cliquez sur **"+ Create Dashboard"**
2. Nommez-le : **"Digital Social Score API - Monitoring"**

### Étape 3: Ajouter les 6 Widgets

#### Widget 1️⃣ : Requêtes API par minute

1. Cliquez **"Add Widget"** → **"Line Chart"**
2. **Configuration** :
   - Resource type: `Prometheus Target`
   - Metric: `prometheus.googleapis.com/toxicity_api_requests_total/counter`
   - Filter: (aucun filtre nécessaire)
   - Aggregation: 
     - Aligner: `rate`
     - Alignment period: `1 minute`
     - Reducer: `sum`
     - Group by: `status`
3. **Titre** : "Requêtes API par minute"
4. Cliquez **"Apply"**

#### Widget 2️⃣ : Distribution des Scores de Toxicité

1. **"Add Widget"** → **"Stacked Area Chart"**
2. **Configuration** :
   - Resource type: `Prometheus Target`
   - Metric: `prometheus.googleapis.com/toxicity_score_distribution/histogram`
   - Aggregation:
     - Aligner: `delta`
     - Alignment period: `1 minute`
     - Reducer: `sum`
     - Group by: `le` (buckets)
3. **Titre** : "Distribution des scores de toxicité"
4. Cliquez **"Apply"**

#### Widget 3️⃣ : Temps de Traitement (Percentiles)

1. **"Add Widget"** → **"Line Chart"**
2. **Ajouter 3 séries de données** :

   **Série 1 - P50** :
   - Metric: `prometheus.googleapis.com/toxicity_processing_seconds/histogram`
   - Aggregation:
     - Aligner: `delta`
     - Reducer: `50th percentile`
   - Legend: "P50"

   **Série 2 - P95** :
   - Même métrique
   - Reducer: `95th percentile`
   - Legend: "P95"

   **Série 3 - P99** :
   - Même métrique
   - Reducer: `99th percentile`
   - Legend: "P99"

3. **Titre** : "Temps de traitement (P50, P95, P99)"
4. Cliquez **"Apply"**

#### Widget 4️⃣ : Utilisateurs Actifs

1. **"Add Widget"** → **"Line Chart"**
2. **Configuration** :
   - Resource type: `Prometheus Target`
   - Metric: `prometheus.googleapis.com/toxicity_api_active_users/gauge`
   - Aggregation:
     - Aligner: `mean`
     - Reducer: `sum`
3. **Titre** : "Utilisateurs actifs"
4. Cliquez **"Apply"**

#### Widget 5️⃣ : Utilisation Mémoire

1. **"Add Widget"** → **"Line Chart"**
2. **Configuration** :
   - Resource type: `Prometheus Target`
   - Metric: `prometheus.googleapis.com/process_resident_memory_bytes/gauge`
   - Aggregation:
     - Aligner: `mean`
     - Reducer: `mean`
3. **Titre** : "Utilisation mémoire (Bytes)"
4. Cliquez **"Apply"**

#### Widget 6️⃣ : Taux d'Erreurs HTTP

1. **"Add Widget"** → **"Scorecard"**
2. **Configuration** :
   - Resource type: `Prometheus Target`
   - Metric: `prometheus.googleapis.com/toxicity_api_requests_total/counter`
   - Filter: `status = "error"`
   - Aggregation:
     - Aligner: `rate`
     - Reducer: `sum`
   - **Thresholds** :
     - Yellow: > 0.01 (1%)
     - Red: > 0.05 (5%)
3. **Titre** : "Taux d'erreurs HTTP"
4. Cliquez **"Apply"**

### Étape 4: Sauvegarder le Dashboard

1. Cliquez sur **"Save"** en haut à droite
2. Le dashboard est maintenant disponible !

## 🧪 Générer Plus de Métriques (Tests de Charge)

Pour visualiser les graphiques en temps réel, lancez des tests de charge :

```powershell
cd etape5-load-testing

# Test de 5 minutes avec 50 utilisateurs
locust -f locustfile.py `
    --host=http://34.38.214.124 `
    --users 50 `
    --spawn-rate 10 `
    --run-time 5m `
    --headless `
    --html test_dashboard_5min.html
```

Pendant le test :
- Rafraîchissez le dashboard toutes les 30 secondes
- Les métriques apparaîtront progressivement
- Prenez des captures d'écran pour votre rapport

## 📸 Captures d'Écran à Prendre

1. **Vue d'ensemble du dashboard** avec les 6 widgets
2. **Widget Requêtes** montrant le pic de charge
3. **Widget Distribution** montrant la répartition des scores
4. **Widget Temps de traitement** avec P50/P95/P99
5. **Metrics Explorer** montrant les métriques brutes

## 🔍 Vérifier que les Métriques Fonctionnent

### Méthode 1: Via Metrics Explorer

1. Ouvrez : https://console.cloud.google.com/monitoring/metrics-explorer?project=digitalsocialscoreapi
2. Cherchez : `prometheus.googleapis.com`
3. Vous devriez voir :
   - ✅ `toxicity_api_requests_total/counter`
   - ✅ `toxicity_score_distribution/histogram`
   - ✅ `toxicity_processing_seconds/histogram`
   - ✅ `toxicity_api_active_users/gauge`
   - ✅ `process_resident_memory_bytes/gauge`

### Méthode 2: Via kubectl (depuis le pod)

```powershell
kubectl exec -n digital-social-score deployment/dss-api-deployment -- `
    python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/metrics').read().decode())" | `
    Select-String "toxicity_api_requests_total"
```

### Méthode 3: Via l'API publique

```powershell
curl http://34.38.214.124/metrics | Select-String "toxicity"
```

## ⚠️ Dépannage

### Les métriques n'apparaissent pas dans Cloud Monitoring

1. **Attendre 2-3 minutes** : Le scraping Prometheus a un délai de propagation
2. **Vérifier PodMonitoring** :
   ```powershell
   kubectl get podmonitoring -n digital-social-score
   kubectl describe podmonitoring dss-api-prometheus -n digital-social-score
   ```
3. **Générer du trafic** :
   ```powershell
   curl -X POST http://34.38.214.124/analyze `
       -H "Content-Type: application/json" `
       -d '{"text":"Hello world"}'
   ```

### Le dashboard est vide

1. **Vérifier la période** : Sélectionnez "Last 1 hour" en haut à droite
2. **Relancer des tests** pour générer de nouvelles données
3. **Vérifier les filtres** : Pas de filtres trop restrictifs sur les widgets

## 📊 Résultats Attendus

Avec 50 utilisateurs pendant 5 minutes :
- **~15,000 requêtes** totales
- **Débit** : ~50 requêtes/seconde
- **Latence P50** : < 50ms
- **Latence P95** : < 200ms
- **Latence P99** : < 500ms
- **Taux d'erreur** : < 1%

## 🎓 Pour le Rapport

Documentez :
1. Les 6 widgets créés avec captures d'écran
2. Les valeurs des métriques pendant la charge
3. Le comportement de l'API sous charge
4. Les limites observées (si applicable)

## ✅ Checklist Complète

- [ ] Dashboard créé avec 6 widgets
- [ ] Métriques Prometheus visibles dans Metrics Explorer
- [ ] Tests de charge exécutés (5 minutes minimum)
- [ ] Captures d'écran prises
- [ ] Données exportées pour le rapport
- [ ] Grille d'évaluation remplie

---

**💡 Astuce** : Gardez le dashboard ouvert pendant les tests et rafraîchissez-le régulièrement pour voir les métriques en temps réel !
