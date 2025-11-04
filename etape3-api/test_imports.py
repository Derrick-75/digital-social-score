#!/usr/bin/env python3
"""
Test d'imports pour diagnostiquer les problèmes
"""

def test_imports():
    print("🔍 Test des imports...")
    
    try:
        import sys
        print(f"✅ Python path: {sys.path[:3]}...")
        
        import fastapi
        print(f"✅ FastAPI version: {fastapi.__version__}")
        
        import uvicorn
        print("✅ Uvicorn imported")
        
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        
        import transformers
        print(f"✅ Transformers version: {transformers.__version__}")
        
        import sklearn
        print(f"✅ Scikit-learn version: {sklearn.__version__}")
        
        import pandas
        print(f"✅ Pandas version: {pandas.__version__}")
        
        import numpy
        print(f"✅ NumPy version: {numpy.__version__}")
        
        import psutil
        print(f"✅ Psutil version: {psutil.__version__}")
        
        print("\n🔍 Test d'import du module app...")
        
        # Test import config
        from app.config import API_TITLE, BERT_MODEL_PATH
        print(f"✅ Config imported - API Title: {API_TITLE}")
        print(f"✅ BERT Model Path: {BERT_MODEL_PATH}")
        
        # Test import models
        from app.models import AnalyzeRequest, AnalyzeResponse
        print("✅ Pydantic models imported")
        
        # Test import inference
        from app.inference import ModelPredictor
        print("✅ Inference module imported")
        
        print("\n✅ Tous les imports sont OK !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()
