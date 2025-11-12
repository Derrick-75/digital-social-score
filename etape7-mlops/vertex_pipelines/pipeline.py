"""
Pipeline Vertex AI - Digital Social Score MLOps
Pipeline complet: Preparation -> Entrainement -> Evaluation
"""

from kfp import dsl, compiler
import sys
from pathlib import Path

# Ajouter le dossier parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

# Import des composants
from components.prepare_data import prepare_data_op
from components.train_model import train_model_op
from components.evaluate_model import evaluate_and_decide_op


@dsl.pipeline(
    name="digital-social-score-ml-pipeline",
    description="Pipeline MLOps pour Digital Social Score - BERT pour detection de toxicite",
    pipeline_root="gs://digitalsocialscoreapi_cloudbuild/vertex-pipelines"
)
def ml_pipeline(
    raw_data_gcs_path: str = "gs://digitalsocialscoreapi_cloudbuild/data/train_sample.csv",
    test_data_gcs_path: str = "gs://digitalsocialscoreapi_cloudbuild/data/test_sample.csv",
    epochs: int = 2
):
    """
    Pipeline MLOps complet
    
    Etapes:
    1. prepare_data_op: Anonymisation NER + nettoyage
    2. train_model_op: Fine-tuning BERT
    3. evaluate_and_decide_op: Evaluation + decision deploiement
    
    Args:
        raw_data_gcs_path: Chemin GCS vers train.csv
        test_data_gcs_path: Chemin GCS vers test.csv
        epochs: Nombre d'epoques d'entrainement (defaut: 2)
    """
    
    # ========================================
    # ETAPE 1: Preparation des donnees
    # ========================================
    prepare_task = prepare_data_op(
        raw_data_gcs_path=raw_data_gcs_path
    )
    
    # ========================================
    # ETAPE 2: Entrainement du modele
    # ========================================
    train_task = train_model_op(
        training_data=prepare_task.outputs['anonymized_data'],
        epochs=epochs
    )
    
    # ========================================
    # ETAPE 3: Evaluation et decision
    # ========================================
    evaluate_task = evaluate_and_decide_op(
        test_data_gcs_path=test_data_gcs_path,
        new_model=train_task.outputs['model_output'],
        current_model_f1=0.5,
        improvement_threshold=0.02
    )


def compile_pipeline(output_file: str = "ml_pipeline.json"):
    """
    Compile le pipeline en fichier JSON
    
    Args:
        output_file: Nom du fichier de sortie
    """
    print("=" * 60)
    print("COMPILATION DU PIPELINE MLOPS")
    print("=" * 60)
    
    try:
        compiler.Compiler().compile(
            pipeline_func=ml_pipeline,
            package_path=output_file
        )
        
        # Calculer la taille
        from pathlib import Path
        size_kb = Path(output_file).stat().st_size / 1024
        
        print(f"\nSUCCES! Pipeline compile:")
        print(f"  Fichier: {output_file}")
        print(f"  Taille:  {size_kb:.2f} KB")
        print("\n" + "=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nERREUR lors de la compilation:")
        print(f"  {e}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    # Compilation du pipeline
    success = compile_pipeline()
    exit(0 if success else 1)
