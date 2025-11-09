#!/usr/bin/env python3
"""
Script pour lancer le pipeline MLOps nettoyé sur Vertex AI
"""
from google.cloud import aiplatform

print("Lancement du pipeline MLOps nettoyé sur Vertex AI...")
print("Project: digitalsocialscoreapi")
print("Region: europe-west1")

# Initialiser Vertex AI
aiplatform.init(
    project="digitalsocialscoreapi",
    location="europe-west1"
)

# Créer le job de pipeline avec le fichier nettoyé
job = aiplatform.PipelineJob(
    display_name="digital-social-score-ml-pipeline",
    template_path="vertex_pipelines/ml_pipeline_clean.json",
    pipeline_root="gs://digitalsocialscoreapi_cloudbuild/vertex-pipelines",
    parameter_values={
        'raw_data_gcs_path': 'gs://digitalsocialscoreapi_cloudbuild/data/train.csv',
        'test_data_gcs_path': 'gs://digitalsocialscoreapi_cloudbuild/data/test.csv',
        'epochs': 2
    },
    enable_caching=False
)

print(f"\nSoumission du pipeline...")
job.submit()

print(f"\n{'='*60}")
print(f"Pipeline lancé avec succès!")
print(f"{'='*60}")
print(f"Nom: {job.display_name}")
print(f"Resource name: {job.resource_name}")
print(f"\nSuivez l'exécution sur:")
print(f"https://console.cloud.google.com/vertex-ai/pipelines?project=digitalsocialscoreapi")
print(f"\nVérifiez les logs de chaque composant dans la console Vertex AI")
