from kfp.v2.dsl import component, Input, Output, Dataset, Model

@component(
    base_image="python:3.10-slim"
)
def train_model_op(training_data: Input[Dataset], epochs: int, model_output: Output[Model]):
    """
    Entraîne un modèle BERT sur les données.
    Args:
        training_data: Dataset anonymisé
        epochs: nombre d'époques
        model_output: modèle entraîné
    """
    import pandas as pd
    import torch
    from transformers import BertForSequenceClassification, BertTokenizer, Trainer, TrainingArguments
    import os
    df = pd.read_csv(training_data.path)
    # Tokenizer et modèle
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertForSequenceClassification.from_pretrained("bert-base-uncased")
    # Préparation des données (simplifiée)
    # ...
    # Entraînement fictif (à adapter selon ton vrai code)
    # model.save_pretrained(model_output.path)
    with open(os.path.join(model_output.path, "dummy.txt"), "w") as f:
        f.write("dummy model")
