"""
Script pour lancer le pipeline MLOps sur Vertex AI
"""

from google.cloud import aiplatform
from datetime import datetime

# Configuration GCP
PROJECT_ID = "digitalsocialscoreapi"
REGION = "europe-west1"
PIPELINE_ROOT = "gs://digitalsocialscoreapi_cloudbuild/vertex-pipelines"
SERVICE_ACCOUNT = "24274638091-compute@developer.gserviceaccount.com"

def launch_pipeline(
    pipeline_json: str = "vertex_pipelines/ml_pipeline.json",
    epochs: int = 2
):
    """
    Lance le pipeline MLOps sur Vertex AI
    
    Args:
        pipeline_json: Chemin vers le pipeline compile
        epochs: Nombre d'epoques d'entrainement
    """
    print("=" * 60)
    print("LANCEMENT DU PIPELINE MLOPS SUR VERTEX AI")
    print("=" * 60)
    
    print(f"\nConfiguration:")
    print(f"  Project:  {PROJECT_ID}")
    print(f"  Region:   {REGION}")
    print(f"  Pipeline: {pipeline_json}")
    print(f"  Epochs:   {epochs}")
    
    try:
        # Initialiser Vertex AI
        aiplatform.init(
            project=PROJECT_ID,
            location=REGION
        )
        
        # Creer le job de pipeline
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        job_id = f"digital-social-score-ml-pipeline-{timestamp}"
        
        print(f"\nCreation du pipeline job...")
        print(f"  Job ID: {job_id}")
        
        job = aiplatform.PipelineJob(
            display_name=job_id,
            template_path=pipeline_json,
            pipeline_root=PIPELINE_ROOT,
            parameter_values={
                "raw_data_gcs_path": "gs://digitalsocialscoreapi_cloudbuild/data/train.csv",
                "test_data_gcs_path": "gs://digitalsocialscoreapi_cloudbuild/data/test.csv",
                "epochs": epochs
            },
            enable_caching=False
        )
        
        print(f"\nLancement du pipeline...")
        job.submit(service_account=SERVICE_ACCOUNT)
        
        print(f"\nSUCCES! Pipeline lance:")
        print(f"  Job ID:   {job.resource_name}")
        print(f"  Console:  https://console.cloud.google.com/vertex-ai/pipelines/runs")
        print(f"\nLe pipeline va s'executer pendant ~40-60 minutes.")
        print(f"Vous pouvez suivre l'execution dans la console Vertex AI.")
        print("=" * 60)
        
        return job
        
    except Exception as e:
        print(f"\nERREUR lors du lancement:")
        print(f"  {e}")
        print("=" * 60)
        raise


if __name__ == "__main__":
    import sys
    
    # Lire le nombre d'epoques depuis les arguments
    epochs = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    
    # Lancer le pipeline
    launch_pipeline(epochs=epochs)
