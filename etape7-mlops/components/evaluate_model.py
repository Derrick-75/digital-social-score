from kfp.v2.dsl import component, Input, Model

@component(
    base_image="python:3.10-slim"
)
def evaluate_and_decide_op(test_data_gcs_path: str, new_model: Input[Model], current_model_f1: float, improvement_threshold: float):
    """
    Evalue le modèle et décide du déploiement.
    Args:
        test_data_gcs_path: Chemin GCS vers le CSV de test
        new_model: modèle entraîné
        current_model_f1: F1-score du modèle actuel
        improvement_threshold: seuil d'amélioration
    """
    import pandas as pd
    import gcsfs
    fs = gcsfs.GCSFileSystem()
    with fs.open(test_data_gcs_path) as f:
        df = pd.read_csv(f)
    # Simulation d'évaluation
    new_f1 = 0.6  # à remplacer par vrai calcul
    if new_f1 > current_model_f1 + improvement_threshold:
        print("Nouveau modèle à déployer !")
    else:
        print("Pas d'amélioration suffisante.")
