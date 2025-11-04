"""
Tests unitaires pour la logique d'inférence
"""
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch
from app.inference import ModelPredictor

class TestModelPredictor:
    """Tests pour la classe ModelPredictor"""
    
    def test_predictor_initialization(self):
        """Test de l'initialisation du prédicteur"""
        predictor = ModelPredictor()
        assert predictor.bert_model is None
        assert predictor.bert_tokenizer is None
        assert predictor.simple_model is None
        assert predictor.tfidf_vectorizer is None
        assert predictor.models_loaded == {}
    
    def test_clean_text_light(self):
        """Test du nettoyage léger de texte"""
        predictor = ModelPredictor()
        
        # Texte avec URL
        text = "Check this out: https://example.com great article!"
        cleaned = predictor.clean_text_light(text)
        assert "https://example.com" not in cleaned
        assert "great article" in cleaned
        
        # Texte avec espaces multiples
        text = "This  has   multiple    spaces"
        cleaned = predictor.clean_text_light(text)
        assert "  " not in cleaned
        
        # Texte vide
        assert predictor.clean_text_light("") == ""
        assert predictor.clean_text_light("   ") == ""
    
    def test_clean_text_full(self):
        """Test du nettoyage complet de texte"""
        predictor = ModelPredictor()
        
        # Texte complexe
        text = "Hello @user! Check https://example.com #hashtag This is TOXIC!!! 123"
        cleaned = predictor.clean_text_full(text)
        
        # Vérifications
        assert "@user" not in cleaned
        assert "https://example.com" not in cleaned
        assert "#hashtag" not in cleaned
        assert "123" not in cleaned
        assert cleaned.islower()
        assert "hello" in cleaned
        assert "toxic" in cleaned
    
    def test_text_validation(self):
        """Test de validation des textes d'entrée"""
        predictor = ModelPredictor()
        
        # Texte None
        assert predictor.clean_text_light(None) == ""
        assert predictor.clean_text_full(None) == ""
        
        # Texte non-string
        assert predictor.clean_text_light(123) == ""
        assert predictor.clean_text_full(123) == ""
    
    @patch('app.inference.BERT_MODEL_PATH')
    @patch('transformers.AutoTokenizer.from_pretrained')
    @patch('transformers.AutoModelForSequenceClassification.from_pretrained')
    def test_load_bert_model_success(self, mock_model, mock_tokenizer, mock_path):
        """Test du chargement réussi du modèle BERT"""
        # Configuration des mocks
        mock_path.exists.return_value = True
        mock_tokenizer.return_value = Mock()
        mock_model.return_value = Mock()
        
        predictor = ModelPredictor()
        result = predictor.load_bert_model()
        
        assert result is True
        assert predictor.models_loaded['bert'] is True
        assert predictor.bert_tokenizer is not None
        assert predictor.bert_model is not None
    
    @patch('app.inference.BERT_MODEL_PATH')
    def test_load_bert_model_not_found(self, mock_path):
        """Test du chargement BERT quand le modèle n'existe pas"""
        mock_path.exists.return_value = False
        
        predictor = ModelPredictor()
        result = predictor.load_bert_model()
        
        assert result is False
        assert predictor.models_loaded.get('bert') is False
    
    def test_get_model_info(self):
        """Test de récupération des informations sur les modèles"""
        predictor = ModelPredictor()
        info = predictor.get_model_info()
        
        assert "device" in info
        assert "models_loaded" in info
        assert isinstance(info["models_loaded"], dict)
    
    def test_is_model_loaded(self):
        """Test de vérification du chargement des modèles"""
        predictor = ModelPredictor()
        
        # Aucun modèle chargé au début
        assert predictor.is_model_loaded("bert") is False
        assert predictor.is_model_loaded("simple") is False
        
        # Simuler un modèle chargé
        predictor.models_loaded["bert"] = True
        assert predictor.is_model_loaded("bert") is True

class TestPredictMethods:
    """Tests pour les méthodes de prédiction"""
    
    def test_predict_invalid_model(self):
        """Test avec un modèle invalide"""
        predictor = ModelPredictor()
        
        with pytest.raises(ValueError, match="Modèle non supporté"):
            predictor.predict("test text", "invalid_model")
    
    def test_predict_long_text_truncation(self):
        """Test de troncature pour texte trop long"""
        predictor = ModelPredictor()
        
        # Créer un texte très long
        long_text = "a" * 10000
        
        # Mock des méthodes pour éviter d'avoir besoin des vrais modèles
        with patch.object(predictor, 'predict_bert') as mock_bert:
            mock_bert.return_value = (0.5, 0.8, {"toxic": 0.5, "severe_toxic": 0.0, "obscene": 0.0, "threat": 0.0, "insult": 0.0, "identity_hate": 0.0})
            
            result = predictor.predict(long_text, "bert")
            
            # Vérifier que le texte passé au modèle est tronqué
            called_text = mock_bert.call_args[0][0]
            assert len(called_text) <= 5000  # MAX_TEXT_LENGTH

class TestMockPredictions:
    """Tests avec des prédictions mockées"""
    
    def test_prediction_output_structure(self):
        """Test de la structure de sortie des prédictions"""
        predictor = ModelPredictor()
        
        # Mock d'une prédiction BERT
        with patch.object(predictor, 'predict_bert') as mock_bert:
            mock_bert.return_value = (
                0.7,  # toxic_prob
                0.9,  # confidence
                {
                    "toxic": 0.7,
                    "severe_toxic": 0.3,
                    "obscene": 0.5,
                    "threat": 0.1,
                    "insult": 0.6,
                    "identity_hate": 0.2
                }
            )
            
            result = predictor.predict("test text", "bert")
            
            # Vérifier la structure
            expected_keys = [
                "score", "toxicity_level", "confidence", 
                "categories", "model_used", "processing_time_ms"
            ]
            for key in expected_keys:
                assert key in result
            
            # Vérifier les types et ranges
            assert isinstance(result["score"], int)
            assert 0 <= result["score"] <= 100
            assert result["toxicity_level"] in ["low", "medium", "high", "extreme"]
            assert 0.0 <= result["confidence"] <= 1.0
            assert result["model_used"] == "bert"
            assert result["processing_time_ms"] > 0
            
            # Vérifier les catégories
            categories = result["categories"]
            for cat_name, cat_value in categories.items():
                assert 0.0 <= cat_value <= 1.0
    
    def test_toxicity_level_calculation(self):
        """Test du calcul des niveaux de toxicité"""
        predictor = ModelPredictor()
        
        test_cases = [
            (0.1, "low"),     # 10% -> low
            (0.3, "medium"),  # 30% -> medium
            (0.7, "high"),    # 70% -> high
            (0.9, "extreme")  # 90% -> extreme
        ]
        
        for toxic_prob, expected_level in test_cases:
            with patch.object(predictor, 'predict_bert') as mock_bert:
                mock_bert.return_value = (
                    toxic_prob, 0.9, 
                    {"toxic": toxic_prob, "severe_toxic": 0.0, "obscene": 0.0, 
                     "threat": 0.0, "insult": 0.0, "identity_hate": 0.0}
                )
                
                result = predictor.predict("test", "bert")
                assert result["toxicity_level"] == expected_level
                assert result["score"] == int(toxic_prob * 100)
