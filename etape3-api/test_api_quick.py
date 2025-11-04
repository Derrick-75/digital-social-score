#!/usr/bin/env python3
"""
Test rapide de l'API Digital Social Score
"""
import sys
import time
import requests
import json
from pathlib import Path

# Ajouter le module app au path
sys.path.append(str(Path(__file__).parent))

def test_api_locally():
    """Test de l'API en local"""
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    print("🔍 Test 1: Health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✅ Health check OK\n")
    except Exception as e:
        print(f"❌ Health check failed: {e}\n")
        return False
    
    # Test 2: Analyze endpoint
    print("🔍 Test 2: Analyze endpoint...")
    test_texts = [
        "Hello, how are you today?",
        "You are such an idiot!",
        "I love this amazing product!"
    ]
    
    for i, text in enumerate(test_texts):
        try:
            payload = {
                "text": text,
                "model_type": "bert"
            }
            
            start_time = time.time()
            response = requests.post(f"{base_url}/analyze", json=payload, timeout=10)
            end_time = time.time()
            
            print(f"Text {i+1}: '{text[:50]}...'")
            print(f"Status: {response.status_code}")
            print(f"Response time: {(end_time - start_time)*1000:.2f}ms")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Toxicity score: {result['toxicity_score']}")
                print(f"Category: {result['toxicity_category']}")
                print("✅ Analysis OK\n")
            else:
                print(f"❌ Error: {response.text}\n")
                
        except Exception as e:
            print(f"❌ Analysis failed: {e}\n")
    
    # Test 3: Stats endpoint
    print("🔍 Test 3: Stats endpoint...")
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"Total requests: {stats['total_requests']}")
            print("✅ Stats OK\n")
        else:
            print(f"❌ Stats error: {response.text}\n")
    except Exception as e:
        print(f"❌ Stats failed: {e}\n")
    
    return True

def test_models_availability():
    """Test de disponibilité des modèles"""
    print("🔍 Test: Model availability...")
    
    from app.config import BERT_MODEL_PATH, SIMPLE_MODEL_PATH
    
    # Test BERT model
    if BERT_MODEL_PATH.exists():
        print(f"✅ BERT model found at: {BERT_MODEL_PATH}")
        
        # Check key files
        required_files = ["config.json", "model.safetensors", "tokenizer.json"]
        for file in required_files:
            if (BERT_MODEL_PATH / file).exists():
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} missing")
    else:
        print(f"❌ BERT model not found at: {BERT_MODEL_PATH}")
    
    # Test Simple model
    if SIMPLE_MODEL_PATH.exists():
        print(f"✅ Simple model found at: {SIMPLE_MODEL_PATH}")
        
        required_files = ["best_simple_model.pkl", "tfidf_vectorizer.pkl"]
        for file in required_files:
            if (SIMPLE_MODEL_PATH / file).exists():
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} missing")
    else:
        print(f"❌ Simple model not found at: {SIMPLE_MODEL_PATH}")

if __name__ == "__main__":
    print("🚀 Digital Social Score API - Test rapide\n")
    
    # Test models first
    test_models_availability()
    print()
    
    # Ask user if they want to start the server
    print("Pour tester l'API, vous devez d'abord démarrer le serveur avec:")
    print("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print()
    
    user_input = input("Le serveur est-il démarré ? (y/n): ")
    if user_input.lower() == 'y':
        test_api_locally()
    else:
        print("Démarrez le serveur et relancez ce script.")
