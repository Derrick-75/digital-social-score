"""
Test rapide de la validation MLOps
"""

print("=" * 60)
print("🚀 TEST RAPIDE MLOps")
print("=" * 60)
print()

# Test 1: Imports
print("1️⃣ Test des imports...")
try:
    import kfp
    from google.cloud import aiplatform
    import pandas as pd
    import sklearn
    print(f"   ✅ kfp {kfp.__version__}")
    print(f"   ✅ aiplatform {aiplatform.__version__}")
    print(f"   ✅ pandas {pd.__version__}")
    print(f"   ✅ sklearn {sklearn.__version__}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    exit(1)

print()

# Test 2: Composants
print("2️⃣ Test des composants...")
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    from vertex_pipelines.components.prepare_data import prepare_data_op
    from vertex_pipelines.components.train_model import train_model_op
    from vertex_pipelines.components.evaluate_model import evaluate_and_decide_op
    
    print("   ✅ prepare_data_op")
    print("   ✅ train_model_op")
    print("   ✅ evaluate_and_decide_op")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print()

# Test 3: Pipeline
print("3️⃣ Test de compilation du pipeline...")
try:
    from vertex_pipelines.pipeline_definition import ml_pipeline, compile_pipeline
    from kfp.v2 import compiler
    
    # Test de compilation
    compiler.Compiler().compile(
        pipeline_func=ml_pipeline,
        package_path="test_pipeline.json"
    )
    
    if os.path.exists("test_pipeline.json"):
        size = os.path.getsize("test_pipeline.json") / 1024
        print(f"   ✅ Pipeline compilé ({size:.1f} KB)")
        os.remove("test_pipeline.json")
    else:
        print("   ❌ Fichier pipeline non créé")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: Données
print("4️⃣ Test des données...")
try:
    train_file = "../etape1-anonymisation/data/raw/train_advanced.csv"
    test_file = "../etape1-anonymisation/data/raw/test_advanced.csv"
    
    if os.path.exists(train_file):
        size = os.path.getsize(train_file) / (1024 * 1024)
        print(f"   ✅ Train: {size:.2f} MB")
    else:
        print(f"   ❌ Train manquant")
    
    if os.path.exists(test_file):
        size = os.path.getsize(test_file) / (1024 * 1024)
        print(f"   ✅ Test: {size:.2f} MB")
    else:
        print(f"   ❌ Test manquant")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print()
print("=" * 60)
print("✨ Tests terminés!")
print("=" * 60)
