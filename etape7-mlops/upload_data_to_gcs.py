"""
Script pour uploader les données d'entraînement vers Google Cloud Storage
Nécessaire pour Vertex AI Pipelines
"""

from google.cloud import storage
import argparse
import os


def upload_training_data(
    project_id: str,
    bucket_name: str = None,
    train_file: str = "etape1-anonymisation/data/raw/train_advanced.csv",
    test_file: str = "etape1-anonymisation/data/raw/test_advanced.csv"
):
    """
    Upload les fichiers de données vers GCS
    
    Args:
        project_id: ID du projet GCP
        bucket_name: Nom du bucket (optionnel, auto-généré si None)
        train_file: Chemin local du fichier d'entraînement
        test_file: Chemin local du fichier de test
    """
    
    if bucket_name is None:
        bucket_name = f"{project_id}_cloudbuild"
    
    print(f"📤 Upload des données vers GCS...")
    print(f"   Bucket: {bucket_name}")
    
    # Initialiser le client Storage
    client = storage.Client(project=project_id)
    
    # Vérifier/créer le bucket
    try:
        bucket = client.get_bucket(bucket_name)
        print(f"✅ Bucket existant: gs://{bucket_name}")
    except Exception:
        print(f"🆕 Création du bucket: gs://{bucket_name}")
        bucket = client.create_bucket(
            bucket_name,
            location="europe-west1"
        )
        print(f"✅ Bucket créé: gs://{bucket_name}")
    
    # Upload des fichiers
    files_to_upload = [
        (train_file, "data/train_advanced.csv"),
        (test_file, "data/test_advanced.csv")
    ]
    
    for local_path, gcs_path in files_to_upload:
        if not os.path.exists(local_path):
            print(f"⚠️  Fichier introuvable: {local_path}")
            continue
        
        # Upload
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_path)
        
        # Taille du fichier
        file_size = os.path.getsize(local_path) / (1024 * 1024)  # MB
        
        print(f"✅ Uploaded: {local_path}")
        print(f"   → gs://{bucket_name}/{gcs_path}")
        print(f"   Size: {file_size:.2f} MB")
    
    print(f"\n🎉 Upload terminé!")
    print(f"\n💡 Vous pouvez maintenant déclencher le pipeline avec:")
    print(f"   python vertex_pipelines/trigger_pipeline.py --project-id {project_id}")


def main():
    """Point d'entrée CLI"""
    parser = argparse.ArgumentParser(
        description="Upload des données d'entraînement vers GCS"
    )
    
    parser.add_argument(
        "--project-id",
        required=True,
        help="ID du projet GCP"
    )
    
    parser.add_argument(
        "--bucket-name",
        help="Nom du bucket GCS (optionnel, auto-généré si omis)"
    )
    
    parser.add_argument(
        "--train-file",
        default="etape1-anonymisation/data/raw/train_advanced.csv",
        help="Chemin local du fichier d'entraînement"
    )
    
    parser.add_argument(
        "--test-file",
        default="etape1-anonymisation/data/raw/test_advanced.csv",
        help="Chemin local du fichier de test"
    )
    
    args = parser.parse_args()
    
    upload_training_data(
        project_id=args.project_id,
        bucket_name=args.bucket_name,
        train_file=args.train_file,
        test_file=args.test_file
    )


if __name__ == "__main__":
    main()
