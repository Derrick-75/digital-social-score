"""
Script de test pour valider les composants Vertex AI Pipelines
Teste chaque composant individuellement avant de lancer le pipeline complet
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test que tous les imports nécessaires fonctionnent"""
    print("🧪 Test des imports...")
    
    try:
        import kfp
        print(f"  ✅ kfp version: {kfp.__version__}")
    except ImportError as e:
        print(f"  ❌ kfp import failed: {e}")
        return False
    
    try:
        from google.cloud import aiplatform
        print(f"  ✅ google-cloud-aiplatform version: {aiplatform.__version__}")
    except ImportError as e:
        print(f"  ❌ google-cloud-aiplatform import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print(f"  ✅ pandas version: {pd.__version__}")
    except ImportError as e:
        print(f"  ❌ pandas import failed: {e}")
        return False
    
    try:
        import sklearn
        print(f"  ✅ scikit-learn version: {sklearn.__version__}")
    except ImportError as e:
        print(f"  ❌ scikit-learn import failed: {e}")
        return False
    
    print("✅ Tous les imports réussis\n")
    return True


def test_component_definitions():
    """Test que les composants peuvent être importés"""
    print("🧪 Test des définitions de composants...")
    
    try:
        from vertex_pipelines.components.prepare_data import prepare_data_component
        print("  ✅ prepare_data_component importé")
    except Exception as e:
        print(f"  ❌ Erreur prepare_data_component: {e}")
        return False
    
    try:
        from vertex_pipelines.components.train_model import train_model_component
        print("  ✅ train_model_component importé")
    except Exception as e:
        print(f"  ❌ Erreur train_model_component: {e}")
        return False
    
    try:
        from vertex_pipelines.components.evaluate_model import evaluate_model_component
        print("  ✅ evaluate_model_component importé")
    except Exception as e:
        print(f"  ❌ Erreur evaluate_model_component: {e}")
        return False
    
    print("✅ Tous les composants importés avec succès\n")
    return True


def test_pipeline_definition():
    """Test que la définition du pipeline est valide"""
    print("🧪 Test de la définition du pipeline...")
    
    try:
        from vertex_pipelines.pipeline_definition import ml_pipeline
        print("  ✅ Pipeline importé")
    except Exception as e:
        print(f"  ❌ Erreur import pipeline: {e}")
        return False
    
    # Tester la compilation
    try:
        from kfp.v2 import compiler
        
        compiler.Compiler().compile(
            pipeline_func=ml_pipeline,
            package_path="test_pipeline.json"
        )
        print("  ✅ Pipeline compilé avec succès")
        
        # Vérifier que le fichier a été créé
        if os.path.exists("test_pipeline.json"):
            file_size = os.path.getsize("test_pipeline.json") / 1024  # KB
            print(f"  ✅ Fichier généré: test_pipeline.json ({file_size:.1f} KB)")
            
            # Nettoyer
            os.remove("test_pipeline.json")
            print("  ✅ Fichier de test nettoyé")
        
    except Exception as e:
        print(f"  ❌ Erreur compilation pipeline: {e}")
        return False
    
    print("✅ Pipeline valide\n")
    return True


def test_data_files():
    """Test que les fichiers de données existent"""
    print("🧪 Test de la présence des données...")
    
    base_path = os.path.join(os.path.dirname(__file__), "..")
    
    train_file = os.path.join(base_path, "etape1-anonymisation", "data", "raw", "train_advanced.csv")
    test_file = os.path.join(base_path, "etape1-anonymisation", "data", "raw", "test_advanced.csv")
    
    if os.path.exists(train_file):
        size = os.path.getsize(train_file) / (1024 * 1024)  # MB
        print(f"  ✅ Train dataset: {size:.2f} MB")
    else:
        print(f"  ❌ Train dataset introuvable: {train_file}")
        return False
    
    if os.path.exists(test_file):
        size = os.path.getsize(test_file) / (1024 * 1024)  # MB
        print(f"  ✅ Test dataset: {size:.2f} MB")
    else:
        print(f"  ❌ Test dataset introuvable: {test_file}")
        return False
    
    print("✅ Fichiers de données présents\n")
    return True


def test_gcp_connection():
    """Test la connexion à GCP"""
    print("🧪 Test de la connexion GCP...")
    
    try:
        from google.cloud import storage
        
        # Essayer de lister les buckets (test de connexion)
        client = storage.Client()
        buckets = list(client.list_buckets(max_results=1))
        
        print(f"  ✅ Connexion GCP établie")
        return True
        
    except Exception as e:
        print(f"  ⚠️  Connexion GCP échouée: {e}")
        print(f"  💡 Exécutez: gcloud auth application-default login")
        return False


def main():
    """Exécute tous les tests"""
    print("=" * 60)
    print("🧪 TESTS DE VALIDATION MLOPS")
    print("=" * 60)
    print()
    
    results = {
        "Imports": test_imports(),
        "Composants": test_component_definitions(),
        "Pipeline": test_pipeline_definition(),
        "Données": test_data_files(),
        "GCP": test_gcp_connection()
    }
    
    print("=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20s}: {status}")
    
    print()
    
    if all(results.values()):
        print("🎉 Tous les tests sont passés!")
        print()
        print("📋 Prochaines étapes:")
        print("1. Uploader les données: python upload_data_to_gcs.py --project-id <PROJECT_ID>")
        print("2. Lancer le pipeline: cd vertex_pipelines && python trigger_pipeline.py --project-id <PROJECT_ID>")
        return 0
    else:
        print("❌ Certains tests ont échoué")
        print()
        print("💡 Actions recommandées:")
        
        if not results["Imports"]:
            print("  - Installer les dépendances: pip install -r requirements.txt")
        
        if not results["GCP"]:
            print("  - Authentifier GCP: gcloud auth application-default login")
        
        if not results["Données"]:
            print("  - Vérifier que les datasets sont dans etape1-anonymisation/data/raw/")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
