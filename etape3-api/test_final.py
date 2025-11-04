#!/usr/bin/env python3
"""
Test final de l'API pour validation complète
"""
import requests
import json
import time

def test_final_api():
    base_url = "http://localhost:8000"
    
    print("🚀 TEST FINAL - API Digital Social Score")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n✅ Test 1: Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Uptime: {data.get('uptime_seconds', 0):.1f}s")
            print(f"   Memory: {data.get('memory_usage_mb', 0):.1f}MB")
            print(f"   Model loaded: {data.get('model_loaded')}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # Test 2: Documentation
    print("\n✅ Test 2: Documentation")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("   Documentation accessible ✓")
        else:
            print(f"   ❌ Documentation: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Documentation: {e}")
    
    # Test 3: Analyse BERT - Texte neutre
    print("\n✅ Test 3: Analyse BERT - Texte Neutre")
    try:
        payload = {"text": "Hello, how are you today? Nice weather!", "model": "bert"}
        start_time = time.time()
        response = requests.post(f"{base_url}/analyze", json=payload, timeout=15)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Score: {result.get('score')}/100")
            print(f"   Niveau: {result.get('toxicity_level')}")
            print(f"   Confiance: {result.get('confidence', 0):.3f}")
            print(f"   Temps: {(end_time - start_time)*1000:.1f}ms")
            print(f"   Modèle: {result.get('model_used')}")
            
            # Vérifier performance
            if (end_time - start_time)*1000 < 500:
                print("   ⚡ Performance OK (<500ms)")
            else:
                print("   ⚠️ Performance lente (>500ms)")
        else:
            print(f"   ❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 4: Analyse BERT - Texte toxique
    print("\n✅ Test 4: Analyse BERT - Texte Toxique")
    try:
        payload = {"text": "You are such an idiot and I hate you!", "model": "bert"}
        start_time = time.time()
        response = requests.post(f"{base_url}/analyze", json=payload, timeout=15)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Score: {result.get('score')}/100")
            print(f"   Niveau: {result.get('toxicity_level')}")
            print(f"   Confiance: {result.get('confidence', 0):.3f}")
            print(f"   Temps: {(end_time - start_time)*1000:.1f}ms")
            
            # Vérifier que c'est détecté comme toxique
            if result.get('score', 0) > 30:
                print("   ✅ Toxicité correctement détectée")
            else:
                print("   ⚠️ Score de toxicité faible")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 5: Analyse Simple - Fallback
    print("\n✅ Test 5: Analyse Modèle Simple")
    try:
        payload = {"text": "This is a test message", "model": "simple"}
        start_time = time.time()
        response = requests.post(f"{base_url}/analyze", json=payload, timeout=15)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Score: {result.get('score')}/100")
            print(f"   Niveau: {result.get('toxicity_level')}")
            print(f"   Temps: {(end_time - start_time)*1000:.1f}ms")
            print(f"   Modèle: {result.get('model_used')}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 6: Validation d'entrée
    print("\n✅ Test 6: Validation d'Entrée")
    try:
        # Texte trop long
        long_text = "a" * 6000
        payload = {"text": long_text, "model": "bert"}
        response = requests.post(f"{base_url}/analyze", json=payload, timeout=15)
        
        if response.status_code == 200:
            print("   ✅ Texte long géré (troncature)")
        elif response.status_code == 422:
            print("   ✅ Validation correcte (422)")
        else:
            print(f"   ⚠️ Réponse inattendue: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 7: Statistiques
    print("\n✅ Test 7: Statistiques")
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"   Total requêtes: {stats.get('total_requests', 0)}")
            print(f"   Temps moyen: {stats.get('average_processing_time_ms', 0):.1f}ms")
            bert_req = stats.get('requests_per_model', {}).get('bert', 0)
            simple_req = stats.get('requests_per_model', {}).get('simple', 0)
            print(f"   BERT: {bert_req}, Simple: {simple_req}")
        else:
            print(f"   ❌ Stats: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stats: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 TESTS TERMINÉS !")
    print("🌐 Documentation: http://localhost:8000/docs")
    print("⚡ Health: http://localhost:8000/health")
    print("📊 Stats: http://localhost:8000/stats")
    
    return True

if __name__ == "__main__":
    test_final_api()
