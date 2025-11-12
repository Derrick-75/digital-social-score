from kfp.v2.dsl import component, Input, Output, Dataset

@component(
    base_image="python:3.10-slim"
)
def prepare_data_op(raw_data_gcs_path: str, anonymized_data: Output[Dataset]):
    """
    Prépare les données : anonymisation et nettoyage.
    Args:
        raw_data_gcs_path: Chemin GCS vers le CSV brut
        anonymized_data: Output Dataset (chemin du CSV anonymisé)
    """
    import pandas as pd
    import os
    import shutil
    import tempfile
    # Simule l'anonymisation (copie le fichier)
    import gcsfs
    fs = gcsfs.GCSFileSystem()
    with fs.open(raw_data_gcs_path) as f:
        df = pd.read_csv(f)
    # Ici, tu pourrais ajouter anonymisation/cleaning
    temp_dir = tempfile.mkdtemp()
    out_path = os.path.join(temp_dir, "anonymized.csv")
    df.to_csv(out_path, index=False)
    shutil.copy(out_path, anonymized_data.path)
