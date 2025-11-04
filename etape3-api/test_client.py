#!/usr/bin/env python3
"""
Client de test pour l'API Digital Social Score
"""
import requests
import json
import time
from typing import Dict, Any

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_health(self) -> bool:
        """Test du endpoint de santé"""
        print("🔍 Test: Health Check")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Status: {data.get('status')}")
                print(f"   Version: {data.get('version')}")
                print("   ✅ Health check OK")
                return True
            else:
                print(f"   ❌ Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False
    
    def test_analyze(self, text: str, model_type: str = "bert") -> Dict[Any, Any]:
        """Test du endpoint d'analyse"""
        print(f"🔍 Test: Analyze - '{text[:50]}...'")
        try:
            payload = {
                "text": text,
                "model_type": model_type
            }
            
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/analyze", 
                json=payload, 
                timeout=30
            )
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            print(f"   Status: {response.status_code}")
            print(f"   Response time: {response_time:.2f}ms")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Toxicity score: {data.get('toxicity_score')}/100")
                print(f"   Category: {data.get('toxicity_category')}")
                print(f"   Is toxic: {data.get('is_toxic')}")
                print("   ✅ Analysis OK")
                return data
            else:
                print(f"   ❌ Error: {response.text}")
                return {}
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return {}
    
    def test_stats(self) -> bool:
        """Test du endpoint de statistiques"""
        print("🔍 Test: Statistics")
        try:
            response = self.session.get(f"{self.base_url}/stats", timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Total requests: {data.get('total_requests', 0)}")
                print(f"   Toxic requests: {data.get('toxic_requests', 0)}")
                print(f"   Avg response time: {data.get('avg_response_time', 0):.2f}ms")
                print("   ✅ Stats OK")
                return True
            else:
                print(f"   ❌ Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False
    
    def test_models_info(self) -> bool:
        """Test du endpoint d'information des modèles"""
        print("🔍 Test: Models Info")
        try:
            response = self.session.get(f"{self.base_url}/models/info", timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Available models: {data.get('available_models', [])}")
                print(f"   Default model: {data.get('default_model')}")
                print("   ✅ Models info OK")
                return True
            else:
                print(f"   ❌ Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            return False
    
    def run_full_test(self):
        """Lance tous les tests"""
        print("🚀 Digital Social Score API - Tests complets\n")
        
        # Tests de base
        results = {
            "health": self.test_health(),
            "models_info": self.test_models_info()
        }
        print()
        
        # Tests d'analyse avec différents textes
        test_texts = [
            ("Hello, how are you today?", "bert"),
            ("You are such an idiot!", "bert"),
            ("I love this amazing product!", "bert"),
            ("This is absolutely terrible and stupid", "simple"),
            ("Thank you for your help, I appreciate it", "simple")
        ]
        
        analysis_results = []
        for text, model in test_texts:
            result = self.test_analyze(text, model)
            analysis_results.append(result)
            print()
        
        # Test des stats après les analyses
        results["stats"] = self.test_stats()
        print()
        
        # Résumé
        print("📊 Résumé des tests:")
        for test_name, success in results.items():
            status = "✅" if success else "❌"
            print(f"   {status} {test_name.title()}")
        
        analyses_ok = sum(1 for r in analysis_results if r)
        print(f"   ✅ Analyses réussies: {analyses_ok}/{len(analysis_results)}")
        
        return all(results.values()) and analyses_ok == len(analysis_results)

def main():
    tester = APITester()
    
    print("Assurez-vous que le serveur API est démarré sur http://localhost:8000")
    input("Appuyez sur Entrée pour continuer...")
    
    success = tester.run_full_test()
    
    if success:
        print("\n🎉 Tous les tests sont passés avec succès!")
    else:
        print("\n⚠️ Certains tests ont échoué. Vérifiez les logs.")

if __name__ == "__main__":
    main()
