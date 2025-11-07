# Étape 5 : Tests de Charge - Digital Social Score API

## 📋 Objectif

Tester la montée en charge de l'API Digital Social Score hébergée sur **http://34.145.51.226** selon les critères de la grille d'évaluation.

## 🎯 Scénarios de Test

| Scénario | Utilisateurs | Durée | Objectif |
|----------|--------------|-------|----------|
| **Montée progressive** | 0 → 500 | 10 min | Comportement en croissance normale |
| **Montée rapide** | 0 → 1000 | 2 min | Réaction à un pic brutal |
| **Pic soudain** | 0 → 800 | 30 sec | Simulation Black Friday |
| **Maintien 300 RPS** | 300 | 30 min | Stabilité sous charge constante |

## 🚀 Installation

### 1. Installer les dépendances

```powershell
cd etape5-load-testing
pip install -r requirements.txt
```

### 2. Vérifier que Locust est installé

```powershell
locust --version
```

Vous devriez voir : `locust 2.20.0` (ou version similaire)

## ⚡ Utilisation

### Test Rapide (5 minutes)

Pour vérifier que tout fonctionne :

```powershell
.\quick_test.ps1
```

Cela va :
- ✅ Vérifier la connectivité avec l'API
- ✅ Envoyer une requête de test
- ✅ Lancer un mini test de charge (10 users, 30s)

### Tests Complets (~1h15)

Pour lancer tous les scénarios de la grille d'évaluation :

```powershell
.\run_tests.ps1
```

**⚠️ Attention** : Les tests vont durer environ **1h15** au total :
- Montée progressive : 10 min
- Montée rapide : 2 min
- Pic soudain : 30 sec
- Maintien 300 RPS : 30 min

### Lancer Locust en mode interactif (optionnel)

Si vous voulez contrôler manuellement les tests avec l'interface web :

```powershell
locust --host=http://34.145.51.226
```

Puis ouvrez http://localhost:8089 dans votre navigateur.

## 📊 Résultats

Les résultats sont générés dans un dossier `results_YYYYMMDD_HHMMSS/` avec :

- **Fichiers HTML** : Graphiques interactifs Locust
- **Fichiers CSV** : Données brutes pour analyse
- **RESUME.txt** : Récapitulatif des tests effectués

### Métriques collectées

Pour chaque scénario, vous aurez :

| Métrique | Description |
|----------|-------------|
| **Requests/s** | Débit (RPS) - nombre de requêtes par seconde |
| **Response Time (ms)** | Latence moyenne |
| **50th percentile** | 50% des requêtes sont plus rapides que X ms |
| **95th percentile** | 95% des requêtes sont plus rapides que X ms |
| **99th percentile** | 99% des requêtes sont plus rapides que X ms |
| **Failure Rate** | Taux d'erreur (%) |
| **Users** | Nombre d'utilisateurs simultanés |

## 📝 Comment Remplir la Grille d'Évaluation

1. **Ouvrez le fichier HTML** de chaque scénario
2. **Notez les métriques** dans le tableau :
   - Débit max (RPS) → Regardez "Total Requests per Second"
   - Latence moyenne (ms) → Regardez "Average Response Time"
   - Taux d'erreur (%) → Regardez "Failures"
3. **Ajoutez vos observations** (ex: "L'API devient lente après 500 users")

### Exemple de tableau rempli

| Scénario | Débit max (RPS) | Latence moyenne (ms) | Taux d'erreur (%) | Observations |
|----------|-----------------|----------------------|-------------------|--------------|
| Montée progressive | 45 | 350 | 2.5 | Dégradation après 300 users |
| Montée rapide | 80 | 850 | 15.0 | Beaucoup d'erreurs 502 |
| Pic soudain | 60 | 1200 | 25.0 | Système saturé |
| Maintien 300 RPS | 42 | 380 | 3.0 | Stable mais lent |

## 💡 Recommandations d'Améliorations

Selon vos résultats, vous devrez proposer des améliorations :

### Si latence > 500ms
- ✅ **Cache Redis** : Mettre en cache les résultats pour les profils identiques
- ✅ **Optimiser le modèle IA** : Réduire la complexité des prédictions

### Si taux d'erreur > 5%
- ✅ **Load Balancer** : Distribuer la charge sur plusieurs instances
- ✅ **Auto-scaling Kubernetes** : Ajouter des pods automatiquement

### Si débit < 50 RPS
- ✅ **Horizontal Scaling** : Augmenter le nombre de réplicas
- ✅ **Optimiser FastAPI** : Utiliser uvicorn avec plusieurs workers

### Pour tous les cas
- ✅ **Monitoring** : Ajouter Prometheus + Grafana
- ✅ **Circuit Breaker** : Éviter la surcharge en rejetant les requêtes
- ✅ **Rate Limiting** : Limiter le nombre de requêtes par client

## 📂 Structure des Fichiers

```
etape5-load-testing/
├── locustfile.py          # Configuration des tests Locust
├── run_tests.ps1          # Script pour lancer tous les scénarios
├── quick_test.ps1         # Test rapide de validation
├── requirements.txt       # Dépendances Python
├── README.md             # Ce fichier
└── results_*/            # Dossiers de résultats (générés)
    ├── montee_progressive_stats.html
    ├── montee_rapide_stats.html
    ├── pic_soudain_stats.html
    ├── maintien_300rps_stats.html
    └── RESUME.txt
```

## 🐛 Dépannage

### Erreur : "locust: command not found"
```powershell
pip install --upgrade locust
```

### Erreur : "Connection refused"
L'API n'est pas accessible. Vérifiez que http://34.145.51.226 fonctionne dans votre navigateur.

### Tests trop longs ?
Modifiez les durées dans `run_tests.ps1` :
- Changez `10m` → `5m`
- Changez `30m` → `10m`

## 📚 Ressources

- [Documentation Locust](https://docs.locust.io/)
- [Grille d'évaluation](../Grille_Evaluation_Tests_Charge.pdf)
- [API Swagger](http://34.145.51.226/docs)

---

**Bon courage pour vos tests ! 🚀**
