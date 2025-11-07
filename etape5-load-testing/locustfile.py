"""
Tests de charge pour l'API Digital Social Score
Teste la détection de toxicité avec différents scénarios
"""
from locust import HttpUser, task, between, events
import random
import logging

# Messages de test avec différents niveaux de toxicité
FRIENDLY_MESSAGES = [
    "This is a great product! I love it!",
    "Thank you so much for your help, I really appreciate it!",
    "The weather is beautiful today, perfect for a walk.",
    "I had an amazing experience with this service!",
    "Great job on the project, keep up the good work!",
    "I completely agree with your point of view.",
    "This is very helpful information, thank you for sharing.",
    "What a wonderful day to learn something new!",
]

NEUTRAL_MESSAGES = [
    "The meeting is scheduled for 3 PM.",
    "I think we should consider other options.",
    "This is an interesting perspective.",
    "Could you please provide more details?",
    "I'm not sure I understand the point.",
    "This requires further investigation.",
    "Let's discuss this in the next meeting.",
]

TOXIC_MESSAGES = [
    "You are stupid and I hate you!",
    "Go kill yourself, nobody likes you!",
    "You are a terrible person and should die!",
    "Shut up you idiot, nobody cares what you think!",
    "You're worthless and pathetic!",
    "I hope you fail miserably!",
    "You're the worst person I've ever met!",
]

class ToxicityAnalysisUser(HttpUser):
    """Utilisateur simulé pour tester l'API de toxicité"""
    wait_time = between(1, 3)  # Attente entre 1 et 3 secondes entre les requêtes
    
    @task(5)
    def analyze_friendly_text(self):
        """Tester avec des messages amicaux (faible toxicité attendue)"""
        text = random.choice(FRIENDLY_MESSAGES)
        self._analyze_text(text, expected_range=(0, 30))
    
    @task(3)
    def analyze_neutral_text(self):
        """Tester avec des messages neutres (toxicité moyenne attendue)"""
        text = random.choice(NEUTRAL_MESSAGES)
        self._analyze_text(text, expected_range=(20, 60))
    
    @task(2)
    def analyze_toxic_text(self):
        """Tester avec des messages toxiques (haute toxicité attendue)"""
        text = random.choice(TOXIC_MESSAGES)
        self._analyze_text(text, expected_range=(50, 100))
    
    def _analyze_text(self, text, expected_range=None):
        """Méthode helper pour analyser un texte"""
        payload = {"text": text, "model": "simple"}
        
        with self.client.post(
            "/analyze", 
            json=payload, 
            headers={"Content-Type": "application/json"}, 
            catch_response=True,
            name="POST /analyze"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Vérifier que la réponse contient un score
                    if "score" in data:
                        score = data["score"]
                        
                        # Optionnel: vérifier que le score est dans la plage attendue
                        if expected_range:
                            min_score, max_score = expected_range
                            if not (min_score <= score <= max_score):
                                logging.warning(
                                    f"Score {score} hors de la plage attendue {expected_range} "
                                    f"pour le texte: {text[:50]}..."
                                )
                        
                        response.success()
                    else:
                        response.failure("Pas de score de toxicité dans la réponse")
                except Exception as e:
                    response.failure(f"Erreur parsing JSON: {str(e)}")
            elif response.status_code == 503:
                response.failure("Service indisponible (503) - Modèle pas chargé?")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def health_check(self):
        """Vérifier la santé de l'API"""
        with self.client.get("/health", catch_response=True, name="GET /health") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") in ["healthy", "degraded"]:
                        response.success()
                    else:
                        response.failure(f"Status inattendu: {data.get('status')}")
                except:
                    response.failure("Réponse health check invalide")
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(1)
    def get_stats(self):
        """Récupérer les statistiques de l'API"""
        with self.client.get("/stats", catch_response=True, name="GET /stats") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Stats failed: {response.status_code}")
    
    @task(1)
    def get_metrics(self):
        """Vérifier l'endpoint Prometheus /metrics"""
        with self.client.get("/metrics", catch_response=True, name="GET /metrics") as response:
            if response.status_code == 200:
                # Vérifier que c'est du format Prometheus
                if "toxicity_api_requests_total" in response.text:
                    response.success()
                else:
                    response.failure("Format Prometheus invalide")
            else:
                response.failure(f"Metrics failed: {response.status_code}")


# Event handlers pour logging personnalisé
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Appelé au démarrage des tests"""
    print("🚀 Démarrage des tests de charge pour Digital Social Score API")
    print(f"🎯 Target: {environment.host}")
    print(f"👥 Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print("=" * 60)


@events.test_stop.add_listener  
def on_test_stop(environment, **kwargs):
    """Appelé à l'arrêt des tests"""
    print("=" * 60)
    print("✅ Tests de charge terminés!")
    print(f"📊 Statistiques disponibles dans le rapport HTML")
    print("💡 Vérifiez également Cloud Monitoring pour les métriques Prometheus")

