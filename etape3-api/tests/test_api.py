import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test de l'endpoint racine"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Digital Social Score API" in data["message"]
    assert "version" in data

def test_health_endpoint():
    """Test du health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data

def test_analyze_valid_text():
    """Test d'analyse avec un texte valide"""
    test_data = {"text": "Hello, this is a nice comment"}
    response = client.post("/analyze", json=test_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "score" in data
    assert "toxicity_level" in data
    assert "categories" in data
    assert "processing_time_ms" in data
    assert 0 <= data["score"] <= 100

def test_analyze_toxic_text():
    """Test d'analyse avec un texte toxique"""
    test_data = {"text": "You are stupid and ugly"}
    response = client.post("/analyze", json=test_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["score"] > 50  # Devrait être toxique

def test_analyze_empty_text():
    """Test avec texte vide"""
    test_data = {"text": ""}
    response = client.post("/analyze", json=test_data)
    assert response.status_code == 422  # Validation error

def test_analyze_too_long_text():
    """Test avec texte trop long"""
    test_data = {"text": "a" * 6000}  # Plus que la limite de 5000
    response = client.post("/analyze", json=test_data)
    assert response.status_code == 422  # Validation error

def test_model_info_endpoint():
    """Test de l'endpoint d'informations du modèle"""
    response = client.get("/model/info")
    assert response.status_code in [200, 503]  # 503 si modèle pas chargé

def test_test_endpoint():
    """Test de l'endpoint de test"""
    response = client.get("/test")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
