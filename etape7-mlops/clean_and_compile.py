#!/usr/bin/env python3
"""
Script pour nettoyer les caractères Unicode problématiques et compiler le pipeline
"""
import json
import sys
from pathlib import Path

# Import des composants
sys.path.append(str(Path(__file__).parent))
from vertex_pipelines.components.prepare_data import prepare_data_op
from vertex_pipelines.components.train_model import train_model_op
from vertex_pipelines.components.evaluate_model import evaluate_and_decide_op

from kfp import dsl, compiler

def clean_string(s):
    """Nettoie une chaîne de caractères des surrogates Unicode"""
    if isinstance(s, str):
        # Remplace les surrogates par des caractères ASCII sûrs
        return s.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
    return s

def clean_dict(d):
    """Nettoie récursivement un dictionnaire"""
    if isinstance(d, dict):
        return {clean_string(k): clean_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [clean_dict(item) for item in d]
    elif isinstance(d, str):
        return clean_string(d)
    return d

@dsl.pipeline(
    name="digital-social-score-ml-pipeline",
    description="Pipeline MLOps pour Digital Social Score - BERT uniquement",
    pipeline_root="gs://digitalsocialscoreapi_cloudbuild/vertex-pipelines"
)
def ml_pipeline(
    raw_data_gcs_path: str = "gs://digitalsocialscoreapi_cloudbuild/data/train.csv",
    test_data_gcs_path: str = "gs://digitalsocialscoreapi_cloudbuild/data/test.csv",
    epochs: int = 2
):
    """Pipeline MLOps complet avec nettoyage Unicode"""
    
    # Étape 1: Préparation des données
    prepare_task = prepare_data_op(
        raw_data_gcs_path=raw_data_gcs_path
    )
    
    # Étape 2: Entraînement du modèle BERT
    train_task = train_model_op(
        training_data=prepare_task.outputs['anonymized_data'],
        epochs=epochs
    )
    
    # Étape 3: Évaluation et décision de déploiement
    evaluate_task = evaluate_and_decide_op(
        test_data_gcs_path=test_data_gcs_path,
        new_model=train_task.outputs['model_output']
    )

if __name__ == "__main__":
    print("=" * 60)
    print("Compilation du pipeline MLOps avec nettoyage Unicode")
    print("=" * 60)
    
    output_file = "vertex_pipelines/ml_pipeline_clean.json"
    
    # Compiler le pipeline
    compiler.Compiler().compile(
        pipeline_func=ml_pipeline,
        package_path=output_file
    )
    
    # Charger et nettoyer le JSON compilé
    print(f"\nNettoyage du fichier compilé...")
    with open(output_file, 'r', encoding='utf-8', errors='replace') as f:
        pipeline_spec = json.load(f)
    
    # Nettoyer récursivement
    cleaned_spec = clean_dict(pipeline_spec)
    
    # Écrire le fichier nettoyé en ASCII pur
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_spec, f, ensure_ascii=True, indent=2)
    
    # Vérifier la taille
    size_kb = Path(output_file).stat().st_size / 1024
    print(f"\nSUCCES! Pipeline compilé et nettoyé: {output_file}")
    print(f"Taille: {size_kb:.2f} KB")
    print("\nVous pouvez maintenant lancer le pipeline avec launch_pipeline_clean.py")
