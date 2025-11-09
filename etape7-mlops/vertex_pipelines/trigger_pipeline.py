"""
Script de déclenchement du pipeline Vertex AI
Utilisé par Cloud Build après un déploiement réussi
"""

import argparse
from datetime import datetime
from google.cloud import aiplatform
from kfp.v2 import compiler


def trigger_pipeline(
    project_id: str,
    region: str,
    model_type: str = "simple",
    epochs: int = 3,
    pipeline_root: str = None,
    display_name: str = None
):
    """
    Déclenche l'exécution du pipeline ML sur Vertex AI
    
    Args:
        project_id: ID du projet GCP
        region: Région GCP (ex: europe-west1)
        model_type: Type de modèle ("simple" ou "bert")
        epochs: Nombre d'époques d'entraînement
        pipeline_root: Racine GCS pour les artefacts
        display_name: Nom d'affichage du pipeline
    """
    
    # Configuration par défaut
    if pipeline_root is None:
        pipeline_root = f"gs://{project_id}_cloudbuild/vertex-pipelines"
    
    if display_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        display_name = f"dss-ml-pipeline-{model_type}-{timestamp}"
    
    print(f"🚀 Déclenchement du pipeline Vertex AI...")
    print(f"   Project: {project_id}")
    print(f"   Region: {region}")
    print(f"   Model Type: {model_type}")
    print(f"   Epochs: {epochs}")
    print(f"   Pipeline Root: {pipeline_root}")
    
    # Initialiser Vertex AI
    aiplatform.init(
        project=project_id,
        location=region
    )
    
    # Compiler le pipeline
    from pipeline_definition import ml_pipeline
    
    compiler.Compiler().compile(
        pipeline_func=ml_pipeline,
        package_path="ml_pipeline.json"
    )
    print("✅ Pipeline compilé")
    
    # Paramètres du pipeline
    pipeline_parameters = {
        "raw_data_gcs_path": f"gs://{project_id}_cloudbuild/data/train_advanced.csv",
        "test_data_gcs_path": f"gs://{project_id}_cloudbuild/data/test_advanced.csv",
        "model_type": model_type,
        "epochs": epochs,
        "batch_size": 16,
        "learning_rate": 2e-5,
        "min_f1_threshold": 0.75,
        "project_id": project_id,
        "region": region
    }
    
    # Créer et soumettre le job
    job = aiplatform.PipelineJob(
        display_name=display_name,
        template_path="ml_pipeline.json",
        pipeline_root=pipeline_root,
        parameter_values=pipeline_parameters,
        enable_caching=True
    )
    
    print(f"📤 Soumission du pipeline job: {display_name}")
    
    # Soumettre (asynchrone)
    job.submit()
    
    print(f"✅ Pipeline soumis avec succès!")
    print(f"   Job Name: {job.resource_name}")
    print(f"   Console URL: https://console.cloud.google.com/vertex-ai/pipelines/runs?project={project_id}")
    print(f"\n💡 Suivez l'exécution dans la console Vertex AI Pipelines")
    
    return job


def main():
    """Point d'entrée CLI"""
    parser = argparse.ArgumentParser(
        description="Déclencher le pipeline ML Vertex AI pour Digital Social Score"
    )
    
    parser.add_argument(
        "--project-id",
        required=True,
        help="ID du projet GCP"
    )
    
    parser.add_argument(
        "--region",
        default="europe-west1",
        help="Région GCP (défaut: europe-west1)"
    )
    
    parser.add_argument(
        "--model-type",
        choices=["simple", "bert"],
        default="simple",
        help="Type de modèle à entraîner (défaut: simple)"
    )
    
    parser.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Nombre d'époques d'entraînement (défaut: 3)"
    )
    
    parser.add_argument(
        "--pipeline-root",
        help="Racine GCS pour les artefacts (optionnel)"
    )
    
    parser.add_argument(
        "--display-name",
        help="Nom d'affichage du pipeline (optionnel)"
    )
    
    args = parser.parse_args()
    
    # Déclencher le pipeline
    trigger_pipeline(
        project_id=args.project_id,
        region=args.region,
        model_type=args.model_type,
        epochs=args.epochs,
        pipeline_root=args.pipeline_root,
        display_name=args.display_name
    )


if __name__ == "__main__":
    main()
