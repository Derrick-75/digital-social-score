#!/usr/bin/env python3
"""
Pipeline MLOps COMPLET - Production ready
"""

from kfp import dsl, compiler
from kfp.dsl import component, Output, Input, Dataset, Model, Metrics
from typing import NamedTuple
from pathlib import Path


# ============================================================
# COMPOSANT 1: Preparation des donnees (TOUTES les donnees)
# ============================================================
@component(
    base_image="python:3.10-slim",
    packages_to_install=[
        "numpy==1.24.3",
        "pandas==2.0.3",
        "google-cloud-storage==2.10.0"
    ]
)
def prepare_data_full(
    raw_data_gcs_path: str,
    prepared_data: Output[Dataset],
    metrics: Output[Metrics],
    max_samples: int = 50000
) -> NamedTuple('Outputs', [('num_samples', int), ('num_toxic', int)]):
    """Prepare les donnees (version complete)"""
    import pandas as pd
    from google.cloud import storage
    
    print("=" * 60)
    print("ETAPE 1: PREPARATION DES DONNEES (COMPLETE)")
    print("=" * 60)
    
    # Charger donnees
    client = storage.Client()
    bucket_name = raw_data_gcs_path.split('/')[2]
    blob_path = '/'.join(raw_data_gcs_path.split('/')[3:])
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.download_to_filename('/tmp/raw_data.csv')
    df = pd.read_csv('/tmp/raw_data.csv')
    print(f"Charge: {len(df)} lignes")
    
    # Nettoyage
    df = df.dropna(subset=['comment_text'])
    df = df[df['comment_text'].str.len() > 10]
    
    # Limiter si necessaire
    if len(df) > max_samples:
        df = df.head(max_samples)
        print(f"Limite a: {max_samples} echantillons")
    
    num_samples = len(df)
    num_toxic = int(df['toxic'].sum())
    
    output_path = prepared_data.path + '.csv'
    df.to_csv(output_path, index=False)
    
    metrics.log_metric('num_samples', num_samples)
    metrics.log_metric('num_toxic', num_toxic)
    metrics.log_metric('toxicity_rate', num_toxic / num_samples)
    
    print(f"TERMINE: {num_samples} echantillons, {num_toxic} toxiques ({100*num_toxic/num_samples:.1f}%)")
    
    from collections import namedtuple
    output = namedtuple('Outputs', ['num_samples', 'num_toxic'])
    return output(num_samples, num_toxic)


# ============================================================
# COMPOSANT 2: Entrainement BERT
# ============================================================
@component(
    base_image="python:3.10-slim",
    packages_to_install=[
        "numpy==1.24.3",
        "pandas==2.0.3",
        "scikit-learn==1.3.0",
        "transformers==4.35.0",
        "torch==2.1.0",
        "accelerate==0.24.1"
    ]
)
def train_model_full(
    training_data: Input[Dataset],
    model_output: Output[Model],
    metrics: Output[Metrics],
    epochs: int = 2,
    batch_size: int = 16,
    learning_rate: float = 2e-5
):
    """Entraine le modele BERT (version complete)"""
    import pandas as pd
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
    import json
    
    print("=" * 60)
    print("ETAPE 2: ENTRAINEMENT BERT COMPLET")
    print("=" * 60)
    
    data_path = training_data.path + '.csv'
    df = pd.read_csv(data_path)
    print(f"Dataset: {len(df)} echantillons")
    
    texts = df['comment_text'].tolist()
    labels = df['toxic'].tolist()
    
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"Train: {len(train_texts)}, Val: {len(val_texts)}")
    
    model_name = "bert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=256)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=256)
    
    class ToxicityDataset(torch.utils.data.Dataset):
        def __init__(self, encodings, labels):
            self.encodings = encodings
            self.labels = labels
        def __getitem__(self, idx):
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item['labels'] = torch.tensor(self.labels[idx])
            return item
        def __len__(self):
            return len(self.labels)
    
    train_dataset = ToxicityDataset(train_encodings, train_labels)
    val_dataset = ToxicityDataset(val_encodings, val_labels)
    
    training_args = TrainingArguments(
        output_dir='/tmp/model_checkpoints',
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_steps=50,
        warmup_steps=100
    )
    
    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = logits.argmax(axis=-1)
        return {
            'accuracy': accuracy_score(labels, predictions),
            'f1': f1_score(labels, predictions, average='binary'),
            'precision': precision_score(labels, predictions, average='binary'),
            'recall': recall_score(labels, predictions, average='binary')
        }
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics
    )
    
    print("Entrainement en cours...")
    train_result = trainer.train()
    eval_result = trainer.evaluate()
    
    print(f"\nResultats finaux:")
    print(f"  Accuracy:  {eval_result['eval_accuracy']:.4f}")
    print(f"  F1:        {eval_result['eval_f1']:.4f}")
    print(f"  Precision: {eval_result['eval_precision']:.4f}")
    print(f"  Recall:    {eval_result['eval_recall']:.4f}")
    
    model_path = model_output.path
    trainer.save_model(model_path)
    tokenizer.save_pretrained(model_path)
    
    with open(f"{model_path}/metadata.json", 'w') as f:
        json.dump({
            'f1_score': float(eval_result['eval_f1']),
            'accuracy': float(eval_result['eval_accuracy']),
            'precision': float(eval_result['eval_precision']),
            'recall': float(eval_result['eval_recall']),
            'epochs': epochs,
            'batch_size': batch_size,
            'learning_rate': learning_rate
        }, f)
    
    metrics.log_metric('accuracy', eval_result['eval_accuracy'])
    metrics.log_metric('f1_score', eval_result['eval_f1'])
    metrics.log_metric('precision', eval_result['eval_precision'])
    metrics.log_metric('recall', eval_result['eval_recall'])
    
    print("TERMINE")


# ============================================================
# PIPELINE COMPLET
# ============================================================
@dsl.pipeline(
    name="digital-social-score-ml-pipeline-full",
    description="Pipeline MLOps complet - Production",
    pipeline_root="gs://digitalsocialscoreapi_cloudbuild/vertex-pipelines"
)
def ml_pipeline_full(
    raw_data_gcs_path: str = "gs://digitalsocialscoreapi_cloudbuild/data/train.csv",
    epochs: int = 2,
    batch_size: int = 16,
    max_samples: int = 50000
):
    """Pipeline MLOps complet"""
    
    # Etape 1: Preparation
    prepare_task = prepare_data_full(
        raw_data_gcs_path=raw_data_gcs_path,
        max_samples=max_samples
    )
    
    # Etape 2: Entrainement
    train_task = train_model_full(
        training_data=prepare_task.outputs['prepared_data'],
        epochs=epochs,
        batch_size=batch_size
    )


# ============================================================
# COMPILATION
# ============================================================
def main():
    print("=" * 60)
    print("COMPILATION DU PIPELINE COMPLET")
    print("=" * 60)
    
    output_file = "ml_pipeline_full.json"
    
    try:
        compiler.Compiler().compile(
            pipeline_func=ml_pipeline_full,
            package_path=output_file
        )
        
        size_kb = Path(output_file).stat().st_size / 1024
        
        print(f"\nSUCCES!")
        print(f"  Fichier: {output_file}")
        print(f"  Taille:  {size_kb:.2f} KB")
        print(f"\nCe pipeline:")
        print(f"  - Jusqu'a 50000 echantillons")
        print(f"  - 2 epoques par defaut")
        print(f"  - Batch size 16")
        print(f"  - Temps estime: 30-45 minutes")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\nERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
