"""
Script pour déclencher le pipeline Vertex AI depuis Cloud Build
"""

import argparse
from google.cloud import aiplatform
from datetime import datetime


def trigger_ml_pipeline(
    project_id: str = "digitalsocialscoreapi",
    region: str = "europe-west1",
    pipeline_root: str = "gs://digitalsocialscoreapi_cloudbuild/vertex-pipelines",
    model_type: str = "simple",
    display_name: str = None
):
    """
    Déclenche l'exécution du pipeline ML Vertex AI
    
    Args:
        project_id: ID du projet GCP
        region: Région GCP
        pipeline_root: Bucket GCS pour les artefacts
        model_type: Type de modèle à entraîner ("simple" ou "bert")
        display_name: Nom d'affichage pour l'exécution du pipeline
    """
    
    print("=" * 60)
    print("🚀 DÉCLENCHEMENT DU PIPELINE MLOPS")
    print("=" * 60)
    
    # Initialisation de Vertex AI
    aiplatform.init(
        project=project_id,
        location=region
    )
    
    # Nom d'affichage avec timestamp
    if display_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        display_name = f"ml-pipeline-{model_type}-{timestamp}"
    
    print(f"\n📋 Configuration:")
    print(f"   Project: {project_id}")
    print(f"   Region: {region}")
    print(f"   Model Type: {model_type}")
    print(f"   Pipeline Root: {pipeline_root}")
    print(f"   Display Name: {display_name}")
    
    # Paramètres du pipeline
    pipeline_params = {
        "raw_data_gcs_path": "gs://digitalsocialscoreapi_cloudbuild/data/train.csv",
        "test_data_gcs_path": "gs://digitalsocialscoreapi_cloudbuild/data/test.csv",
        "model_type": model_type,
        "epochs": 3 if model_type == "simple" else 2,  # Moins d'époques pour BERT (plus lent)
        "batch_size": 32 if model_type == "simple" else 16,
        "learning_rate": 0.001 if model_type == "simple" else 2e-5,
        "min_f1_threshold": 0.75,
        "project_id": project_id,
        "region": region
    }
    
    print(f"\n⚙️  Paramètres du pipeline:")
    for key, value in pipeline_params.items():
        print(f"   {key}: {value}")
    
    try:
        # Création du job de pipeline
        print(f"\n🔄 Création du pipeline job...")
        
        job = aiplatform.PipelineJob(
            display_name=display_name,
            template_path="vertex_pipelines/ml_pipeline.json",  # Fichier compilé
            pipeline_root=pipeline_root,
            parameter_values=pipeline_params,
            enable_caching=True  # Active le cache pour accélérer les réexécutions
        )
        
        print(f"✅ Pipeline job créé: {job.resource_name}")
        
        # Soumission du pipeline
        print(f"\n🚀 Soumission du pipeline...")
        job.submit()
        
        print(f"\n" + "=" * 60)
        print(f"✅ PIPELINE DÉCLENCHÉ AVEC SUCCÈS!")
        print(f"=" * 60)
        print(f"\n📊 Suivez l'exécution sur:")
        print(f"   https://console.cloud.google.com/vertex-ai/pipelines/runs/{job.resource_name}?project={project_id}")
        print(f"\n⏱️  Le pipeline peut prendre 20-60 minutes selon le modèle")
        
        return job
        
    except Exception as e:
        print(f"\n❌ ERREUR lors du déclenchement du pipeline:")
        print(f"   {str(e)}")
        raise


def main():
    """
    Point d'entrée principal
    """
    parser = argparse.ArgumentParser(
        description="Déclenche le pipeline MLOps Vertex AI"
    )
    
    parser.add_argument(
        "--project-id",
        default="digitalsocialscoreapi",
        help="ID du projet GCP"
    )
    
    parser.add_argument(
        "--region",
        default="europe-west1",
        help="Région GCP"
    )
    
    parser.add_argument(
        "--model-type",
        choices=["simple", "bert"],
        default="simple",
        help="Type de modèle à entraîner"
    )
    
    parser.add_argument(
        "--pipeline-root",
        default="gs://digitalsocialscoreapi_cloudbuild/vertex-pipelines",
        help="Bucket GCS pour les artefacts du pipeline"
    )
    
    parser.add_argument(
        "--display-name",
        help="Nom d'affichage personnalisé pour le pipeline"
    )
    
    args = parser.parse_args()
    
    # Déclenche le pipeline
    trigger_ml_pipeline(
        project_id=args.project_id,
        region=args.region,
        pipeline_root=args.pipeline_root,
        model_type=args.model_type,
        display_name=args.display_name
    )


if __name__ == "__main__":
    main()
