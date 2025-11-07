"""
Module pour exporter les métriques Prometheus
Permet de monitorer l'API avec Google Cloud Monitoring ou Grafana
"""
from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator

# Métriques custom pour l'API de toxicité
toxicity_requests = Counter(
    'toxicity_api_requests_total',
    'Nombre total de requêtes d\'analyse de toxicité',
    ['model_type', 'status']
)

toxicity_score = Histogram(
    'toxicity_score_distribution',
    'Distribution des scores de toxicité retournés',
    buckets=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
)

toxicity_processing_time = Histogram(
    'toxicity_processing_seconds',
    'Temps de traitement de l\'analyse de toxicité',
    ['model_type'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

active_users = Gauge(
    'toxicity_api_active_users',
    'Nombre d\'utilisateurs actifs en ce moment'
)

model_load_time = Histogram(
    'model_load_seconds',
    'Temps de chargement des modèles IA',
    ['model_type']
)

# Instrumentator FastAPI pour métriques automatiques
instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="toxicity_api_requests_inprogress",
    inprogress_labels=True,
)

def setup_metrics(app):
    """
    Configure les métriques Prometheus pour l'application FastAPI
    
    Usage:
        from app.metrics import setup_metrics
        setup_metrics(app)
    """
    # Ajouter l'instrumentation automatique
    instrumentator.instrument(app)
    
    # Exposer l'endpoint /metrics
    instrumentator.expose(app, endpoint="/metrics", include_in_schema=False)
    
    return app
