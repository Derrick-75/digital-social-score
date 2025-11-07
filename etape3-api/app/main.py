"""
API FastAPI pour Digital Social Score - Détection de Toxicité
Conforme RGPD - Aucune donnée stockée
"""
import time
import logging
import psutil
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from .config import (
    API_TITLE, API_DESCRIPTION, API_VERSION, 
    ALLOWED_ORIGINS, LOG_LEVEL, LOG_FORMAT
)
from .models import (
    AnalyzeRequest, AnalyzeResponse, ToxicityCategories,
    HealthResponse, ErrorResponse, StatsResponse
)
from .inference import predictor

# ✅ Import des métriques Prometheus (pour monitoring avancé)
try:
    from .metrics import setup_metrics, toxicity_requests, toxicity_score, toxicity_processing_time
    METRICS_ENABLED = True
except ImportError:
    METRICS_ENABLED = False
    # Le logger sera défini plus bas

# ✅ CORRECTION: Configuration du logging sécurisée
try:
    # Convertir le niveau de log en niveau logging approprié
    if isinstance(LOG_LEVEL, str):
        log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    else:
        log_level = LOG_LEVEL
    
    logging.basicConfig(level=log_level, format=LOG_FORMAT)
except (AttributeError, ValueError):
    # Fallback en cas d'erreur
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

logger = logging.getLogger(__name__)

# Variables globales pour les statistiques
app_start_time = time.time()
request_stats = {
    "total_requests": 0,
    "requests_per_model": {"bert": 0, "simple": 0},
    "processing_times": [],
    "toxicity_distribution": {"low": 0, "medium": 0, "high": 0, "extreme": 0},
    "last_request": None
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    logger.info("🚀 Démarrage de l'API Digital Social Score")
    logger.info("📦 Pré-chargement des modèles...")
    
    # Pré-charger le modèle BERT (le plus utilisé)
    try:
        predictor.load_bert_model()
        logger.info("✅ Modèle BERT pré-chargé")
    except Exception as e:
        logger.warning(f"⚠️ Échec du pré-chargement BERT: {e}")
    
    # Pré-charger le modèle simple
    try:
        predictor.load_simple_model()
        logger.info("✅ Modèle simple pré-chargé")
    except Exception as e:
        logger.warning(f"⚠️ Échec du pré-chargement modèle simple: {e}")
    
    logger.info("🎉 API prête à traiter les requêtes")
    
    yield
    
    # Shutdown
    logger.info("🛑 Arrêt de l'API Digital Social Score")

# Création de l'application FastAPI
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ✅ ACTIVATION PROMETHEUS - Métriques disponibles sur /metrics
if METRICS_ENABLED:
    setup_metrics(app)
    logger.info("📊 Métriques Prometheus activées sur /metrics")
else:
    logger.warning("⚠️ Métriques Prometheus désactivées (module non trouvé)")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Middleware pour logging des requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log toutes les requêtes avec timing"""
    start_time = time.time()
    
    # Traiter la requête
    response = await call_next(request)
    
    # Calculer le temps de traitement
    process_time = time.time() - start_time
    
    # Logger la requête
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

def update_stats(model_used: str, processing_time: float, toxicity_level: str):
    """Met à jour les statistiques globales"""
    request_stats["total_requests"] += 1
    request_stats["requests_per_model"][model_used] += 1
    request_stats["processing_times"].append(processing_time)
    request_stats["toxicity_distribution"][toxicity_level] += 1
    request_stats["last_request"] = datetime.now()
    
    # Garder seulement les 1000 derniers temps de traitement
    if len(request_stats["processing_times"]) > 1000:
        request_stats["processing_times"] = request_stats["processing_times"][-1000:]

@app.get("/", tags=["General"])
async def root():
    """Point d'entrée principal de l'API"""
    return {
        "message": "🛡️ Digital Social Score API - Détection de Toxicité",
        "version": API_VERSION,
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "analyze_endpoint": "/analyze"
    }

@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check():
    """Endpoint de vérification de santé de l'API"""
    try:
        uptime = time.time() - app_start_time
        memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Vérifier si au moins un modèle est chargé
        model_loaded = any([
            predictor.is_model_loaded("bert"),
            predictor.is_model_loaded("simple")
        ])
        
        return HealthResponse(
            status="healthy" if model_loaded else "degraded",
            version=API_VERSION,
            model_loaded=model_loaded,
            uptime_seconds=uptime,
            memory_usage_mb=memory_usage
        )
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/models/info", tags=["Models"])
async def models_info():
    """Informations sur les modèles chargés"""
    try:
        return predictor.get_model_info()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des infos modèles: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne")

@app.get("/stats", response_model=StatsResponse, tags=["Monitoring"])
async def get_stats():
    """Statistiques d'utilisation de l'API"""
    try:
        avg_processing_time = (
            sum(request_stats["processing_times"]) / len(request_stats["processing_times"])
            if request_stats["processing_times"] else 0.0
        )
        
        return StatsResponse(
            total_requests=request_stats["total_requests"],
            requests_per_model=request_stats["requests_per_model"],
            average_processing_time_ms=avg_processing_time,
            toxicity_distribution=request_stats["toxicity_distribution"],
            last_request=request_stats["last_request"]
        )
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne")

@app.post("/analyze", response_model=AnalyzeResponse, tags=["AI Analysis"])
async def analyze_toxicity(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks
):
    """
    🎯 **Analyse de Toxicité**
    
    Analyse un texte et retourne un score de toxicité de 0 à 100.
    
    - **text**: Le texte à analyser (max 5000 caractères)    - **model**: Modèle à utiliser ("bert" ou "simple")
    
    **Note RGPD**: Aucune donnée n'est stockée ou logged.
    """
    try:
        logger.info(f"Analyse demandée avec modèle: {request.model}")
        
        # Timer pour Prometheus
        start_time = time.time()
        
        # Effectuer la prédiction
        result = predictor.predict(request.text, request.model)
        
        # ✅ Enregistrer les métriques Prometheus
        if METRICS_ENABLED:
            # Compter la requête
            toxicity_requests.labels(
                model_type=result["model_used"],
                status="success"
            ).inc()
            
            # Enregistrer le score
            toxicity_score.observe(result["score"])
            
            # Enregistrer le temps de traitement
            toxicity_processing_time.labels(
                model_type=result["model_used"]
            ).observe(result["processing_time_ms"] / 1000)  # Convertir ms en secondes
        
        # Créer la réponse
        response = AnalyzeResponse(
            score=result["score"],
            toxicity_level=result["toxicity_level"],
            confidence=result["confidence"],
            categories=ToxicityCategories(**result["categories"]),
            model_used=result["model_used"],
            processing_time_ms=result["processing_time_ms"]
        )
        
        # Mettre à jour les statistiques en arrière-plan
        background_tasks.add_task(
            update_stats,
            result["model_used"],
            result["processing_time_ms"],
            result["toxicity_level"]
        )
        
        logger.info(f"Analyse terminée - Score: {result['score']} - Temps: {result['processing_time_ms']:.1f}ms")
        
        return response
        
    except ValueError as e:
        # ✅ Enregistrer l'erreur dans Prometheus
        if METRICS_ENABLED:
            toxicity_requests.labels(model_type=request.model, status="validation_error").inc()
        logger.warning(f"Erreur de validation: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        # ✅ Enregistrer l'erreur dans Prometheus
        if METRICS_ENABLED:
            toxicity_requests.labels(model_type=request.model, status="model_error").inc()
        logger.error(f"Erreur modèle: {e}")
        raise HTTPException(status_code=503, detail="Modèle temporairement indisponible")
    except Exception as e:
        # ✅ Enregistrer l'erreur dans Prometheus
        if METRICS_ENABLED:
            toxicity_requests.labels(model_type=request.model, status="server_error").inc()
        logger.error(f"Erreur inattendue lors de l'analyse: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire global d'exceptions"""
    logger.error(f"Exception non gérée: {exc}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            message="Une erreur inattendue s'est produite"
        ).model_dump(mode='json')
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Gestionnaire d'exceptions HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=f"HTTP {exc.status_code}",
            message=exc.detail
        ).model_dump(mode='json')
    )

if __name__ == "__main__":
    # ✅ CORRECTION: Gestion sécurisée du log level pour uvicorn
    try:
        uvicorn_log_level = LOG_LEVEL.lower() if isinstance(LOG_LEVEL, str) else "info"
    except:
        uvicorn_log_level = "info"
        
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level=uvicorn_log_level
    )