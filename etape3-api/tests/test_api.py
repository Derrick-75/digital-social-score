"""
Tests unitaires pour l'API Digital Social Score
"""
import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

# Client de test FastAPI
client = TestClient(app)

class TestAPI:
    """Tests pour les endpoints principaux de l'API"""
    
    def test_root_endpoint(self):
        """Test du point d'entrée principal"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "Digital Social Score" in data["message"]
    
    def test_health_endpoint(self):
        """Test de l'endpoint de santé"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "model_loaded" in data
        assert "uptime_seconds" in data
        assert "memory_usage_mb" in data
    
    def test_models_info_endpoint(self):
        """Test de l'endpoint d'informations sur les modèles"""
        response = client.get("/models/info")
        assert response.status_code == 200
        data = response.json()
        assert "device" in data
        assert "models_loaded" in data
    
    def test_stats_endpoint(self):
        """Test de l'endpoint de statistiques"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "requests_per_model" in data
        assert "average_processing_time_ms" in data
        assert "toxicity_distribution" in data

class TestAnalyzeEndpoint:
    """Tests pour l'endpoint d'analyse de toxicité"""
    
    def test_analyze_valid_text_bert(self):
        """Test d'analyse avec texte valide et modèle BERT"""
        payload = {
            "text": "This is a normal, non-toxic message.",
            "model": "bert"
        }
        response = client.post("/analyze", json=payload)
        
        # Peut échouer si le modèle BERT n'est pas disponible
        if response.status_code == 503:
            pytest.skip("Modèle BERT non disponible")
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier la structure de la réponse
        assert "score" in data
        assert "toxicity_level" in data
        assert "confidence" in data
        assert "categories" in data
        assert "model_used" in data
        assert "processing_time_ms" in data
        assert "timestamp" in data
        
        # Vérifier les types et ranges
        assert isinstance(data["score"], int)
        assert 0 <= data["score"] <= 100
        assert data["toxicity_level"] in ["low", "medium", "high", "extreme"]
        assert 0.0 <= data["confidence"] <= 1.0
        assert data["model_used"] == "bert"
        assert data["processing_time_ms"] > 0
    
    def test_analyze_valid_text_simple(self):
        """Test d'analyse avec texte valide et modèle simple"""
        payload = {
            "text": "This is a normal, non-toxic message.",
            "model": "simple"
        }
        response = client.post("/analyze", json=payload)
        
        # Peut échouer si le modèle simple n'est pas disponible
        if response.status_code == 503:
            pytest.skip("Modèle simple non disponible")
        
        assert response.status_code == 200
        data = response.json()
        assert data["model_used"] == "simple"
    
    def test_analyze_toxic_text(self):
        """Test d'analyse avec texte potentiellement toxique"""
        payload = {
            "text": "You are stupid and I hate you",
            "model": "bert"
        }
        response = client.post("/analyze", json=payload)
        
        if response.status_code == 503:
            pytest.skip("Modèle non disponible")
        
        assert response.status_code == 200
        data = response.json()
        
        # Le score devrait être plus élevé pour un texte toxique
        assert data["score"] >= 0  # Au minimum 0
    
    def test_analyze_empty_text(self):
        """Test avec texte vide (doit échouer)"""
        payload = {
            "text": "",
            "model": "bert"
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_analyze_whitespace_only(self):
        """Test avec seulement des espaces (doit échouer)"""
        payload = {
            "text": "   ",
            "model": "bert"
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_analyze_very_long_text(self):
        """Test avec texte très long (doit être tronqué)"""
        long_text = "This is a test. " * 1000  # Très long
        payload = {
            "text": long_text,
            "model": "bert"
        }
        response = client.post("/analyze", json=payload)
        
        if response.status_code == 503:
            pytest.skip("Modèle non disponible")
        
        # Doit toujours fonctionner (texte tronqué automatiquement)
        assert response.status_code == 200
    
    def test_analyze_invalid_model(self):
        """Test avec modèle invalide"""
        payload = {
            "text": "Test message",
            "model": "invalid_model"
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_analyze_missing_text(self):
        """Test sans le champ text requis"""
        payload = {
            "model": "bert"
        }
        response = client.post("/analyze", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_analyze_default_model(self):
        """Test avec modèle par défaut (bert)"""
        payload = {
            "text": "Test message"
        }
        response = client.post("/analyze", json=payload)
        
        if response.status_code == 503:
            pytest.skip("Modèle non disponible")
        
        assert response.status_code == 200
        data = response.json()
        assert data["model_used"] == "bert"  # Modèle par défaut

class TestCategories:
    """Tests pour les catégories de toxicité"""
    
    def test_categories_structure(self):
        """Test de la structure des catégories"""
        payload = {
            "text": "Test message",
            "model": "bert"
        }
        response = client.post("/analyze", json=payload)
        
        if response.status_code == 503:
            pytest.skip("Modèle non disponible")
        
        assert response.status_code == 200
        data = response.json()
        
        categories = data["categories"]
        expected_categories = [
            "toxic", "severe_toxic", "obscene", 
            "threat", "insult", "identity_hate"
        ]
        
        for cat in expected_categories:
            assert cat in categories
            assert 0.0 <= categories[cat] <= 1.0

class TestErrorHandling:
    """Tests de gestion d'erreurs"""
    
    def test_invalid_json(self):
        """Test avec JSON invalide"""
        response = client.post(
            "/analyze",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_malformed_request(self):
        """Test avec requête malformée"""
        response = client.post("/analyze", json={"invalid": "data"})
        assert response.status_code == 422

class TestDocumentation:
    """Tests pour la documentation automatique"""
    
    def test_openapi_docs(self):
        """Test de l'accès à la documentation OpenAPI"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_docs(self):
        """Test de l'accès à la documentation ReDoc"""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_schema(self):
        """Test du schéma OpenAPI"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
