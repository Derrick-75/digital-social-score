"""
Pipeline Vertex AI : MLOps Digital Social Score
Pipeline complet d'entraînement et déploiement automatique
"""

from kfp.v2 import dsl
from kfp.v2.dsl import pipeline
from google.cloud import aiplatform

# Import des composants
from .components.prepare_data import prepare_data_op
from .components.train_model import train_model_op
from .components.evaluate_model import evaluate_and_decide_op


@pipeline(
    name="digital-social-score-ml-pipeline",
    description="Pipeline MLOps pour entraîner et déployer le modèle de détection de toxicité",
    pipeline_root="gs://digitalsocialscoreapi-mlops/vertex-pipelines"
)
def ml_pipeline(
    # Paramètres du pipeline
    raw_data_gcs_path: str = "gs://digitalsocialscoreapi_cloudbuild/data/train.csv",
    test_data_gcs_path: str = "gs://digitalsocialscoreapi_cloudbuild/data/test.csv",
    model_type: str = "simple",  # "simple" ou "bert"
    epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 2e-5,
    min_f1_threshold: float = 0.75,
    project_id: str = "digitalsocialscoreapi",
    region: str = "europe-west1"
):
    """
    Pipeline ML complet pour Digital Social Score
    
    Étapes:
    1. Préparation des données (nettoyage + anonymisation)
    2. Entraînement du modèle (BERT ou Simple)
    3. Évaluation sur dataset de test
    4. Décision de déploiement basée sur F1-score
    5. Déploiement automatique si performances suffisantes
    
    Args:
        raw_data_gcs_path: Chemin GCS des données brutes d'entraînement
        test_data_gcs_path: Chemin GCS des données de test
        model_type: Type de modèle ("simple" ou "bert")
        epochs: Nombre d'époques d'entraînement
        batch_size: Taille des batches
        learning_rate: Taux d'apprentissage
        min_f1_threshold: Seuil F1 minimum pour déployer
        project_id: ID du projet GCP
        region: Région GCP
    """
    
    # ========================================
    # ÉTAPE 1 : Préparation des données
    # ========================================
    prepare_data_task = prepare_data_op(
        raw_data_gcs_path=raw_data_gcs_path
    )
    prepare_data_task.set_display_name("📋 Préparation des données")
    prepare_data_task.set_cpu_limit('2')
    prepare_data_task.set_memory_limit('4G')
    
    # ========================================
    # ÉTAPE 2 : Entraînement du modèle
    # ========================================
    train_model_task = train_model_op(
        training_data=prepare_data_task.outputs['anonymized_data'],
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate
    )
    train_model_task.set_display_name("🤖 Entraînement modèle")
    train_model_task.set_cpu_limit('4')
    train_model_task.set_memory_limit('8G')
    
    # Note: Le modèle type est BERT (codé en dur dans le composant)
    
    # ========================================
    # ÉTAPE 3 : Évaluation du modèle
    # ========================================
    evaluate_model_task = evaluate_and_decide_op(
        test_data_gcs_path=test_data_gcs_path,
        new_model=train_model_task.outputs['model_output'],
        current_model_f1=0.5,  # F1-Score baseline (à ajuster selon votre modèle actuel)
        improvement_threshold=0.02
    )
    evaluate_model_task.set_display_name("📊 Évaluation du modèle")
    evaluate_model_task.set_cpu_limit('2')
    evaluate_model_task.set_memory_limit('4G')
    
    # ========================================
    # ÉTAPE 4 : Déploiement conditionnel
    # ========================================
    # Le déploiement se fera si should_deploy == True
    # Cette logique peut être ajoutée avec une condition dsl
    
    with dsl.Condition(
        evaluate_model_task.outputs['should_deploy'] == True,
        name="deploy-if-good-performance"
    ):
        # Ici on pourrait ajouter un composant de déploiement
        # qui met à jour l'API avec le nouveau modèle
        
        @dsl.component(
            base_image="python:3.10-slim",
            packages_to_install=["google-cloud-storage==2.10.0"]
        )
        def deploy_model_component(
            trained_model: dsl.Input[dsl.Model],
            f1_score: float,
            project_id: str,
            destination_bucket: str = "digitalsocialscoreapi_cloudbuild"
        ):
            """
            Déploie le nouveau modèle vers GCS
            """
            from google.cloud import storage
            import json
            from datetime import datetime
            
            print(f"🚀 Déploiement du nouveau modèle (F1={f1_score:.4f})...")
            
            # Upload vers GCS
            client = storage.Client(project=project_id)
            bucket = client.bucket(destination_bucket)
            
            # Nom avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_path = f"models/deployed/model_{timestamp}"
            
            # Upload des fichiers du modèle
            import os
            for root, dirs, files in os.walk(trained_model.path):
                for file in files:
                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, trained_model.path)
                    blob_path = f"{model_path}/{relative_path}"
                    
                    blob = bucket.blob(blob_path)
                    blob.upload_from_filename(local_path)
                    print(f"  ✅ Uploaded: {blob_path}")
            
            # Marquer comme modèle actif
            active_model_blob = bucket.blob("models/active_model.json")
            active_model_blob.upload_from_string(
                json.dumps({
                    "model_path": model_path,
                    "f1_score": f1_score,
                    "deployed_at": timestamp
                })
            )
            
            print(f"✅ Modèle déployé avec succès vers gs://{destination_bucket}/{model_path}")
        
        deploy_task = deploy_model_component(
            trained_model=train_model_task.outputs['model_output'],
            f1_score=evaluate_model_task.outputs['new_f1_score'],
            project_id=project_id
        )
        deploy_task.set_display_name("🚀 Déploiement du modèle")


# ========================================
# Fonction de compilation du pipeline
# ========================================
def compile_pipeline(output_file: str = "ml_pipeline.json"):
    """
    Compile le pipeline en fichier JSON
    """
    from kfp.v2 import compiler
    
    compiler.Compiler().compile(
        pipeline_func=ml_pipeline,
        package_path=output_file
    )
    
    print(f"✅ Pipeline compilé: {output_file}")


if __name__ == "__main__":
    # Compilation du pipeline
    compile_pipeline()
