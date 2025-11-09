#!/bin/bash
# Script pour déclencher le pipeline MLOps Vertex AI
# Utilisé par Cloud Build

set -e

echo "🚀 Déclenchement du pipeline MLOps Vertex AI..."

# Variables d'environnement
PROJECT_ID=${PROJECT_ID:-"digitalsocialscoreapi"}
REGION=${REGION:-"europe-west1"}
PIPELINE_ROOT="gs://${PROJECT_ID}_cloudbuild/vertex-pipelines"

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -q kfp google-cloud-aiplatform google-cloud-storage

# Compiler le pipeline
echo "🔨 Compilation du pipeline..."
cd /workspace/etape7-mlops/vertex_pipelines
python pipeline_definition.py

# Déclencher le pipeline
echo "▶️  Lancement du pipeline..."
python trigger_pipeline.py \
    --project-id="${PROJECT_ID}" \
    --region="${REGION}" \
    --pipeline-root="${PIPELINE_ROOT}"

echo "✅ Pipeline MLOps déclenché avec succès!"
echo "📊 Suivez l'exécution sur: https://console.cloud.google.com/vertex-ai/pipelines"
