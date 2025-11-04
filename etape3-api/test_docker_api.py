#!/usr/bin/env python3
"""
Test spécifique pour l'API Docker
"""
import requests
import time

def test_docker_api():
    base_url = "http://localhost:8001"  # Port Docker
    
    print("🐳 TEST API DOCKER - Digital Social Score")
    print("=" * 60)
    
    # Attendre que le container soit prêt
    print("⏳ Attente du démarrage du container...")
    time.sleep(5)
    
    # Test Health Check
    print("\n✅ Test 1: Health Check Docker")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Model loaded: {data.get('model_loaded')}")
            print(f"   Memory: {data.get('memory_usage_mb', 0):.1f}MB")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # Test Documentation
    print("\n✅ Test 2: Documentation Docker")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("   ✅ Documentation accessible")
        else:
            print(f"   ❌ Documentation: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Documentation: {e}")
    
    # Test Analyse Simple
    print("\n✅ Test 3: Analyse Simple avec Docker")
    try:
        payload = {"text": "Hello world! This is a test.", "model": "simple"}
        start_time = time.time()
        response = requests.post(f"{base_url}/analyze", json=payload, timeout=20)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Score: {result.get('score')}/100")
            print(f"   📊 Niveau: {result.get('toxicity_level')}")
            print(f"   ⚡ Temps: {(end_time - start_time)*1000:.1f}ms")
            print(f"   🤖 Modèle: {result.get('model_used')}")
        else:
            print(f"   ❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test Performance
    print("\n✅ Test 4: Performance Docker")
    response_times = []
    for i in range(3):
        try:
            payload = {"text": f"Test message number {i+1}", "model": "simple"}
            start_time = time.time()
            response = requests.post(f"{base_url}/analyze", json=payload, timeout=20)
            end_time = time.time()
            
            if response.status_code == 200:
                response_times.append((end_time - start_time) * 1000)
                print(f"   Requête {i+1}: {response_times[-1]:.1f}ms")
        except Exception as e:
            print(f"   ❌ Requête {i+1}: {e}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        print(f"   📊 Temps moyen: {avg_time:.1f}ms")
        if avg_time < 500:
            print("   ✅ Performance OK (<500ms)")
        else:
            print("   ⚠️ Performance lente (>500ms)")
    
    print("\n" + "=" * 60)
    print("🎉 TESTS DOCKER TERMINÉS !")
    print(f"🌐 API Docker: {base_url}")
    print(f"📖 Documentation: {base_url}/docs")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_docker_api()
