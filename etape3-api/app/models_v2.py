"""
Schémas Pydantic pour l'API Digital Social Score - Compatible Pydantic v2
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Dict, Optional, List
from datetime import datetime

class AnalyzeRequest(BaseModel):
    """Requête d'analyse de toxicité"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    text: str = Field(
        ..., 
        min_length=1, 
        max_length=5000, 
        description="Texte à analyser pour la toxicité"
    )
    model: Optional[str] = Field(
        "bert", 
        description="Modèle à utiliser: 'bert' ou 'simple'",
        pattern="^(bert|simple)$"
    )
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        """Valide et nettoie le texte d'entrée"""
        if not v or not v.strip():
            raise ValueError("Le texte ne peut pas être vide")
        return v.strip()

class ToxicityCategories(BaseModel):
    """Scores détaillés par catégorie de toxicité"""
    toxic: float = Field(ge=0.0, le=1.0, description="Score toxicité générale")
    severe_toxic: float = Field(ge=0.0, le=1.0, description="Toxicité sévère")
    obscene: float = Field(ge=0.0, le=1.0, description="Contenu obscène")
    threat: float = Field(ge=0.0, le=1.0, description="Menaces")
    insult: float = Field(ge=0.0, le=1.0, description="Insultes")
    identity_hate: float = Field(ge=0.0, le=1.0, description="Haine identitaire")

class AnalyzeResponse(BaseModel):
    """Réponse d'analyse de toxicité"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    score: int = Field(
        ge=0, 
        le=100, 
        description="Score de toxicité de 0 (non-toxique) à 100 (très toxique)"
    )
    toxicity_level: str = Field(
        description="Niveau de toxicité: low, medium, high, extreme"
    )
    confidence: float = Field(
        ge=0.0, 
        le=1.0, 
        description="Confiance du modèle dans la prédiction"
    )
    categories: ToxicityCategories = Field(
        description="Scores détaillés par catégorie"
    )
    model_used: str = Field(description="Modèle utilisé pour l'analyse")
    processing_time_ms: float = Field(
        description="Temps de traitement en millisecondes"
    )
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Horodatage de l'analyse"
    )

class HealthResponse(BaseModel):
    """Réponse du endpoint de santé"""
    status: str = Field(description="Statut de l'API")
    version: str = Field(description="Version de l'API")
    model_loaded: bool = Field(description="Indique si le modèle est chargé")
    uptime_seconds: float = Field(description="Temps de fonctionnement en secondes")
    memory_usage_mb: float = Field(description="Utilisation mémoire en MB")

class ErrorResponse(BaseModel):
    """Réponse d'erreur standardisée"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    error: str = Field(description="Type d'erreur")
    message: str = Field(description="Message d'erreur détaillé")
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Horodatage de l'erreur"
    )

class StatsResponse(BaseModel):
    """Statistiques de l'API"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )
    
    total_requests: int = Field(description="Nombre total de requêtes")
    requests_per_model: Dict[str, int] = Field(description="Requêtes par modèle")
    average_processing_time_ms: float = Field(description="Temps moyen de traitement")
    toxicity_distribution: Dict[str, int] = Field(description="Distribution des niveaux de toxicité")
    last_request: Optional[datetime] = Field(default=None, description="Dernière requête")
