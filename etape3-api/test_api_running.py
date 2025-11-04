#!/usr/bin/env python3
"""
Test simple de l'API en cours d'exécution
"""
import requests
import json
import time

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Test rapide de l'API Digital Social Score")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n🔍 Test 1: Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Status: {health_data.get('status', 'unknown')}")
            print(f"📊 Uptime: {health_data.get('uptime_seconds', 0):.1f}s")
        else:
            print(f"❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Analyze text (Simple case)
    print("\n🔍 Test 2: Analyze Simple Text")
    try:
        payload = {
            "text": "Hello, how are you today?",
            "model": "bert"
        }
        
        start_time = time.time()
        response = requests.post(f"{base_url}/analyze", json=payload, timeout=15)
        end_time = time.time()
        
        print(f"Status: {response.status_code}")
        print(f"Response Time: {(end_time - start_time)*1000:.1f}ms")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Toxicity Score: {result.get('toxicity_score', 'N/A')}")
            print(f"📊 Category: {result.get('toxicity_category', 'N/A')}")
            print(f"🤖 Model: {result.get('model_used', 'N/A')}")
        else:
            print(f"❌ Analysis failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False
    
    # Test 3: Analyze toxic text
    print("\n🔍 Test 3: Analyze Toxic Text")
    try:
        payload = {
            "text": "You are such an idiot and I hate you!",
            "model": "bert"
        }
        
        start_time = time.time()
        response = requests.post(f"{base_url}/analyze", json=payload, timeout=15)
        end_time = time.time()
        
        print(f"Status: {response.status_code}")
        print(f"Response Time: {(end_time - start_time)*1000:.1f}ms")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Toxicity Score: {result.get('toxicity_score', 'N/A')}")
            print(f"📊 Category: {result.get('toxicity_category', 'N/A')}")
            print(f"⚠️ Is Toxic: {result.get('is_toxic', 'N/A')}")
        else:
            print(f"❌ Toxic analysis failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Toxic analysis error: {e}")
    
    # Test 4: Documentation
    print("\n🔍 Test 4: Documentation Access")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Documentation accessible at http://localhost:8000/docs")
        else:
            print(f"❌ Documentation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Documentation error: {e}")
    
    # Test 5: Stats
    print("\n🔍 Test 5: Statistics")
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Total Requests: {stats.get('total_requests', 0)}")
            print(f"📊 Average Response Time: {stats.get('average_response_time_ms', 0):.1f}ms")
        else:
            print(f"❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés !")
    print("🌐 API Documentation: http://localhost:8000/docs")
    print("⚡ Health Check: http://localhost:8000/health")
    
    return True

if __name__ == "__main__":
    test_api()
