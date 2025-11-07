"""
Logique d'inférence pour les modèles de détection de toxicité
"""
import torch
import json
import pickle
import time
import logging
from pathlib import Path
from typing import Tuple, Dict, Optional
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import re

from .config import BERT_MODEL_PATH, SIMPLE_MODEL_PATH, MAX_TEXT_LENGTH, TOXICITY_LEVELS

logger = logging.getLogger(__name__)

class ModelPredictor:
    """Classe pour gérer les prédictions des modèles"""
    
    def __init__(self):
        self.bert_model = None
        self.bert_tokenizer = None
        self.simple_model = None
        self.tfidf_vectorizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.models_loaded = {}
        
        logger.info(f"Initialisation du prédicteur sur device: {self.device}")
    
    def load_bert_model(self) -> bool:
        """Charge le modèle BERT fine-tuné"""
        try:
            if self.bert_model is not None:
                return True
                
            logger.info("Chargement du modèle BERT...")
            
            # Vérifier que les fichiers existent
            if not BERT_MODEL_PATH.exists():
                logger.error(f"Modèle BERT non trouvé: {BERT_MODEL_PATH}")
                return False
            
            # Charger le tokenizer et le modèle
            self.bert_tokenizer = AutoTokenizer.from_pretrained(str(BERT_MODEL_PATH))
            self.bert_model = AutoModelForSequenceClassification.from_pretrained(
                str(BERT_MODEL_PATH)
            )
            self.bert_model.to(self.device)
            self.bert_model.eval()
            
            self.models_loaded['bert'] = True
            logger.info("✅ Modèle BERT chargé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement BERT: {str(e)}")
            self.models_loaded['bert'] = False
            return False
    
    def load_simple_model(self) -> bool:
        """Charge le modèle simple (TF-IDF + Logistic Regression)"""
        try:
            if self.simple_model is not None:
                return True
                
            logger.info("Chargement du modèle simple...")
              # Chemins des fichiers
            model_path = SIMPLE_MODEL_PATH / "best_simple_model.pkl"
            vectorizer_path = SIMPLE_MODEL_PATH / "tfidf_vectorizer.pkl"
            
            if not model_path.exists() or not vectorizer_path.exists():
                logger.warning(f"Fichiers du modèle simple non trouvés, création d'un modèle dummy")
                return self.create_dummy_simple_model()
            
            # Charger le modèle et le vectorizer
            with open(model_path, 'rb') as f:
                self.simple_model = pickle.load(f)
            
            with open(vectorizer_path, 'rb') as f:
                self.tfidf_vectorizer = pickle.load(f)
            
            self.models_loaded['simple'] = True
            logger.info("✅ Modèle simple chargé avec succès")
            return True
            
        except Exception as e:
            logger.warning(f"Erreur lors du chargement du modèle simple: {str(e)}")
            logger.info("Création d'un modèle simple dummy pour les tests")
            return self.create_dummy_simple_model()
    
    def create_dummy_simple_model(self) -> bool:
        """Crée un modèle simple dummy pour les tests"""
        try:
            logger.info("Création d'un modèle simple dummy...")
            
            # Créer un modèle et vectorizer dummy
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            import numpy as np
            
            # Données d'entraînement minimales
            dummy_texts = [
                "hello good day", "love you", "great fantastic wonderful",
                "hate you idiot", "stupid fool moron", "damn hell shit"
            ]
            dummy_labels = [0, 0, 0, 1, 1, 1]  # 0=non-toxic, 1=toxic
            
            # Entraîner un modèle très simple
            self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            X = self.tfidf_vectorizer.fit_transform(dummy_texts)
            
            self.simple_model = LogisticRegression(random_state=42)
            self.simple_model.fit(X, dummy_labels)
            
            self.models_loaded['simple'] = True
            logger.info("✅ Modèle simple dummy créé avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du modèle dummy: {str(e)}")
            self.models_loaded['simple'] = False
            return False
    
    def clean_text_light(self, text: str) -> str:
        """Nettoyage léger du texte (comme pour BERT)"""
        if not isinstance(text, str):
            return ""
        
        # Supprimer les URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Trim
        text = text.strip()
        
        return text
    
    def clean_text_full(self, text: str) -> str:
        """Nettoyage complet du texte (pour modèle simple)"""
        if not isinstance(text, str):
            return ""
        
        text = str(text)
        
        # Minuscules
        text = text.lower()
        
        # Supprimer les URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Supprimer les mentions (@username)
        text = re.sub(r'@\w+', '', text)
        
        # Supprimer les hashtags (#hashtag)
        text = re.sub(r'#\w+', '', text)
        
        # Supprimer les caractères non alphabétiques (garder espaces)
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Trim
        text = text.strip()
        
        return text
    
    def predict_bert(self, text: str) -> Tuple[float, float, Dict]:
        """Prédiction avec le modèle BERT"""
        if not self.load_bert_model():
            raise RuntimeError("Modèle BERT non disponible")
        
        # Nettoyer le texte
        cleaned_text = self.clean_text_light(text)
        
        # Tokeniser
        inputs = self.bert_tokenizer(
            cleaned_text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        ).to(self.device)
        
        # Prédiction
        with torch.no_grad():
            outputs = self.bert_model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            toxic_prob = probabilities[0, 1].item()
            confidence = torch.max(probabilities, dim=1)[0].item()
        
        # Créer des scores détaillés (simulés pour BERT binaire)
        categories = {
            'toxic': toxic_prob,
            'severe_toxic': toxic_prob * 0.7 if toxic_prob > 0.8 else 0.0,
            'obscene': toxic_prob * 0.8 if toxic_prob > 0.6 else 0.0,
            'threat': toxic_prob * 0.5 if toxic_prob > 0.9 else 0.0,
            'insult': toxic_prob * 0.9 if toxic_prob > 0.5 else 0.0,
            'identity_hate': toxic_prob * 0.6 if toxic_prob > 0.7 else 0.0
        }
        
        return toxic_prob, confidence, categories
    
    def predict_simple(self, text: str) -> Tuple[float, float, Dict]:
        """Prédiction avec le modèle simple"""
        if not self.load_simple_model():
            raise RuntimeError("Modèle simple non disponible")
        
        # Nettoyer le texte
        cleaned_text = self.clean_text_full(text)
        
        # Vectoriser
        X = self.tfidf_vectorizer.transform([cleaned_text])
        
        # Prédiction
        prob = self.simple_model.predict_proba(X)[0, 1]
        confidence = max(self.simple_model.predict_proba(X)[0])
        
        # Créer des scores détaillés (simulés)
        categories = {
            'toxic': prob,
            'severe_toxic': prob * 0.6 if prob > 0.8 else 0.0,
            'obscene': prob * 0.7 if prob > 0.6 else 0.0,
            'threat': prob * 0.4 if prob > 0.9 else 0.0,
            'insult': prob * 0.8 if prob > 0.5 else 0.0,
            'identity_hate': prob * 0.5 if prob > 0.7 else 0.0
        }
        
        return prob, confidence, categories
    
    def predict(self, text: str, model_name: str = "bert") -> Dict:
        """Prédiction unifiée"""
        start_time = time.time()
        
        # Valider la longueur du texte
        if len(text) > MAX_TEXT_LENGTH:
            text = text[:MAX_TEXT_LENGTH]
        
        try:
            # Choisir le modèle
            if model_name == "bert":
                toxic_prob, confidence, categories = self.predict_bert(text)
            elif model_name == "simple":
                toxic_prob, confidence, categories = self.predict_simple(text)
            else:
                raise ValueError(f"Modèle non supporté: {model_name}")
            
            # Calculer le score (0-100)
            score = int(toxic_prob * 100)
            
            # Déterminer le niveau de toxicité
            toxicity_level = "low"
            for level, (min_score, max_score) in TOXICITY_LEVELS.items():
                if min_score <= score < max_score:
                    toxicity_level = level
                    break
            
            # Temps de traitement
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "score": score,
                "toxicity_level": toxicity_level,
                "confidence": confidence,
                "categories": categories,
                "model_used": model_name,
                "processing_time_ms": processing_time
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {str(e)}")
            raise
    
    def is_model_loaded(self, model_name: str) -> bool:
        """Vérifie si un modèle est chargé"""
        return self.models_loaded.get(model_name, False)
    
    def get_model_info(self) -> Dict:
        """Retourne les informations sur les modèles chargés"""
        info = {
            "device": str(self.device),
            "models_loaded": self.models_loaded.copy()
        }
        
        # Ajouter les métadonnées si disponibles
        try:
            if BERT_MODEL_PATH.exists():
                metadata_path = BERT_MODEL_PATH / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        info["bert_metadata"] = json.load(f)
        except Exception:
            pass
        
        try:
            if SIMPLE_MODEL_PATH.exists():
                metadata_path = SIMPLE_MODEL_PATH / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        info["simple_metadata"] = json.load(f)
        except Exception:
            pass
        
        return info

# Instance globale du prédicteur
predictor = ModelPredictor()
