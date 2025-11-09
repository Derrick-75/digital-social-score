"""
Script pour compiler le pipeline Vertex AI en fichier JSON
"""

import sys
import os

# Ajouter le dossier vertex_pipelines au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'vertex_pipelines'))

from kfp.v2 import compiler
from vertex_pipelines.pipeline_definition import ml_pipeline


def compile_pipeline():
    """
    Compile le pipeline ML en fichier JSON
    """
    print("=" * 60)
    print("🔧 COMPILATION DU PIPELINE MLOPS")
    print("=" * 60)
    
    output_file = "vertex_pipelines/ml_pipeline.json"
    
    print(f"\n📝 Compilation en cours...")
    print(f"   Fichier source: vertex_pipelines/pipeline_definition.py")
    print(f"   Fichier de sortie: {output_file}")
    
    try:
        # Compilation
        compiler.Compiler().compile(
            pipeline_func=ml_pipeline,
            package_path=output_file
        )
        
        # Vérification
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / 1024  # Ko
            print(f"\n✅ COMPILATION RÉUSSIE!")
            print(f"   Fichier: {output_file}")
            print(f"   Taille: {file_size:.2f} Ko")
            print(f"\n📋 Le pipeline est prêt à être déployé sur Vertex AI")
            return True
        else:
            print(f"\n❌ ERREUR: Le fichier compilé n'a pas été créé")
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR lors de la compilation:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = compile_pipeline()
    sys.exit(0 if success else 1)
