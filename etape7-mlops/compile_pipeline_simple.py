"""
Script de compilation simplifié du pipeline MLOps
Compatible avec KFP 2.14.6
"""

import sys
import os

# Ajouter le répertoire au path
sys.path.insert(0, os.path.dirname(__file__))

from kfp import dsl, compiler
from vertex_pipelines.components.prepare_data import prepare_data_op
from vertex_pipelines.components.train_model import train_model_op
from vertex_pipelines.components.evaluate_model import evaluate_and_decide_op


@dsl.pipeline(
    name="digital-social-score-ml-pipeline",
    description="Pipeline MLOps pour detection de toxicite"
)
def ml_pipeline(
    raw_data_gcs_path: str = "gs://digitalsocialscoreapi_cloudbuild/data/train.csv",
    test_data_gcs_path: str = "gs://digitalsocialscoreapi_cloudbuild/data/test.csv",
    epochs: int = 2
):
    """Pipeline ML complet"""
    
    # Etape 1: Preparation des donnees
    prepare_data_task = prepare_data_op(
        raw_data_gcs_path=raw_data_gcs_path
    )
    
    # Etape 2: Entrainement BERT
    train_model_task = train_model_op(
        training_data=prepare_data_task.outputs['anonymized_data'],
        epochs=epochs
    )
    
    # Etape 3: Evaluation
    evaluate_model_task = evaluate_and_decide_op(
        test_data_gcs_path=test_data_gcs_path,
        new_model=train_model_task.outputs['model_output']
    )


def main():
    output_file = "vertex_pipelines/ml_pipeline.json"
    
    print("=" * 60)
    print("Compilation du pipeline MLOps")
    print("=" * 60)
    
    try:
        compiler.Compiler().compile(
            pipeline_func=ml_pipeline,
            package_path=output_file
        )
        
        if os.path.exists(output_file):
            size_kb = os.path.getsize(output_file) / 1024
            print(f"\nSUCCES! Pipeline compile: {output_file}")
            print(f"Taille: {size_kb:.2f} KB")
            return True
        else:
            print(f"\nERREUR: Fichier non cree")
            return False
    except Exception as e:
        print(f"\nERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
