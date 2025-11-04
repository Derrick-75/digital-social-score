#!/usr/bin/env python3
"""
Script de validation complète de l'API Digital Social Score
Tests automatisés pour valider tous les critères
"""
import requests
import json
import time
import sys
from typing import Dict, List, Tuple

class APIValidator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        
    def log_test(self, name: str, success: bool, message: str, response_time: float = 0):
        """Enregistre le résultat d'un test"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "name": name,
            "success": success,
            "message": message,
            "response_time": response_time
        })
        print(f"{status} {name}: {message}")
        if response_time > 0:
            print(f"   ⏱️  Response time: {response_time:.1f}ms")
    
    def test_health_check(self) -> bool:
        """Test du endpoint de santé"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}", response_time)
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_analyze_safe_text(self) -> bool:
        """Test avec un texte non-toxique"""
        payload = {
            "text": "Hello, how are you today? This is a wonderful day!",
            "model": "bert"
        }
        return self._test_analyze("Safe Text Analysis", payload, expected_toxic=False)
    
    def test_analyze_toxic_text(self) -> bool:
        """Test avec un texte toxique"""
        payload = {
            "text": "You are such an idiot and I hate you!",
            "model": "bert"
        }
        return self._test_analyze("Toxic Text Analysis", payload, expected_toxic=True)
    
    def test_simple_model(self) -> bool:
        """Test avec le modèle simple"""
        payload = {
            "text": "This is a test for the simple model.",
            "model": "simple"
        }
        return self._test_analyze("Simple Model Test", payload)
    
    def _test_analyze(self, test_name: str, payload: Dict, expected_toxic: bool = None) -> bool:
        """Test générique pour l'endpoint analyze"""
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/analyze", 
                json=payload, 
                timeout=15
            )
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                score = data.get('toxicity_score', 0)
                is_toxic = data.get('is_toxic', False)
                
                # Vérifier le temps de réponse (< 500ms)
                if response_time < 500:
                    time_check = "✅"
                else:
                    time_check = "⚠️"
                
                message = f"Score: {score}, Toxic: {is_toxic}, Time: {time_check}"
                
                # Vérifier si le résultat correspond à l'attendu
                if expected_toxic is not None:
                    if (expected_toxic and is_toxic) or (not expected_toxic and not is_toxic):
                        self.log_test(test_name, True, message, response_time)
                        return True
                    else:
                        self.log_test(test_name, False, f"Expected toxic={expected_toxic}, got {is_toxic}", response_time)
                        return False
                else:
                    self.log_test(test_name, True, message, response_time)
                    return True
            else:
                self.log_test(test_name, False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(test_name, False, f"Error: {str(e)}")
            return False
    
    def test_validation_errors(self) -> bool:
        """Test des erreurs de validation"""
        tests = [
            ("Empty text", {"text": "", "model": "bert"}),
            ("Invalid model", {"text": "Test", "model": "invalid"}),
            ("Missing text", {"model": "bert"}),
            ("Too long text", {"text": "x" * 6000, "model": "bert"})
        ]
        
        all_passed = True
        for test_name, payload in tests:
            try:
                response = self.session.post(f"{self.base_url}/analyze", json=payload, timeout=10)
                if response.status_code == 422:
                    self.log_test(f"Validation - {test_name}", True, "Correctly rejected")
                else:
                    self.log_test(f"Validation - {test_name}", False, f"Expected 422, got {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Validation - {test_name}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_stats_endpoint(self) -> bool:
        """Test du endpoint de statistiques"""
        try:
            response = self.session.get(f"{self.base_url}/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                total_requests = data.get('total_requests', 0)
                self.log_test("Statistics", True, f"Total requests: {total_requests}")
                return True
            else:
                self.log_test("Statistics", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Statistics", False, f"Error: {str(e)}")
            return False
    
    def test_model_info(self) -> bool:
        """Test du endpoint d'informations sur les modèles"""
        try:
            response = self.session.get(f"{self.base_url}/models/info", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get('available_models', [])
                self.log_test("Model Info", True, f"Available models: {models}")
                return True
            else:
                self.log_test("Model Info", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Model Info", False, f"Error: {str(e)}")
            return False
    
    def test_documentation(self) -> bool:
        """Test d'accès à la documentation"""
        try:
            response = self.session.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                self.log_test("Documentation", True, "Swagger UI accessible")
                return True
            else:
                self.log_test("Documentation", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Documentation", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self) -> bool:
        """Exécute tous les tests de validation"""
        print("🧪 VALIDATION COMPLÈTE DE L'API DIGITAL SOCIAL SCORE")
        print("=" * 60)
        
        # Tests essentiels
        tests = [
            ("Health Check", self.test_health_check),
            ("Safe Text Analysis", self.test_analyze_safe_text),
            ("Toxic Text Analysis", self.test_analyze_toxic_text),
            ("Simple Model", self.test_simple_model),
            ("Validation Errors", self.test_validation_errors),
            ("Statistics", self.test_stats_endpoint),
            ("Model Info", self.test_model_info),
            ("Documentation", self.test_documentation)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            if test_func():
                passed += 1
        
        # Résumé
        print("\n" + "=" * 60)
        print(f"📊 RÉSULTATS: {passed}/{total} tests passés")
        
        if passed == total:
            print("🎉 TOUS LES TESTS SONT PASSÉS !")
            print("✅ L'API est prête pour la production")
        else:
            print(f"⚠️  {total - passed} test(s) ont échoué")
            print("❌ L'API nécessite des corrections")
        
        # Calcul des temps de réponse
        response_times = [r['response_time'] for r in self.results if r['response_time'] > 0]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            print(f"\n⏱️  PERFORMANCE:")
            print(f"   Temps moyen: {avg_time:.1f}ms")
            print(f"   Temps maximum: {max_time:.1f}ms")
            print(f"   Critère < 500ms: {'✅' if max_time < 500 else '❌'}")
        
        return passed == total

def main():
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    print(f"🎯 Testing API at: {base_url}")
    
    validator = APIValidator(base_url)
    success = validator.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
