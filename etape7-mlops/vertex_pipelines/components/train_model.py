"""
Composant Vertex AI : Entraînement du modèle BERT
Ce composant entraîne un modèle BERT pour la détection de toxicité
"""

from kfp.dsl import component, Input, Output, Dataset, Model, Metrics


@component(
    base_image="python:3.10-slim",
    packages_to_install=[
        "pandas==2.0.3",
        "scikit-learn==1.3.0",
        "transformers==4.35.0",
        "torch==2.1.0",
        "accelerate==0.24.1"
    ]
)
def train_model_op(
    training_data: Input[Dataset],
    model_output: Output[Model],
    metrics: Output[Metrics],
    epochs: int = 3,
    learning_rate: float = 2e-5,
    batch_size: int = 16
):
    """
    Entraîne un modèle BERT pour la classification de toxicité
    
    Args:
        training_data: Dataset d'entraînement anonymisé
        model_output: Modèle entraîné en sortie
        metrics: Métriques d'entraînement
        epochs: Nombre d'époques d'entraînement
        learning_rate: Taux d'apprentissage
        batch_size: Taille du batch
    """
    import pandas as pd
    import torch
    from transformers import (
        AutoTokenizer, 
        AutoModelForSequenceClassification,
        Trainer,
        TrainingArguments
    )
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, f1_score
    import json
    
    print("🤖 Début de l'entraînement du modèle BERT...")
    
    # Charger les données
    data_path = training_data.path + '.csv'
    df = pd.read_csv(data_path)
    
    print(f"📊 Dataset chargé: {len(df)} échantillons")
    
    # Préparer les données
    texts = df['text_anonymized'].tolist()
    labels = df['toxic'].tolist() if 'toxic' in df.columns else [0] * len(df)
    
    # Split train/val
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"✂️  Split: {len(train_texts)} train, {len(val_texts)} validation")
    
    # Charger le tokenizer et modèle pré-entraîné
    model_name = "bert-base-uncased"
    print(f"📥 Chargement du modèle pré-entraîné: {model_name}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=2
    )
    
    # Tokenization
    print("🔤 Tokenization des textes...")
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=512)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=512)
    
    # Créer les datasets PyTorch
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
    
    # Configuration de l'entraînement
    training_args = TrainingArguments(
        output_dir='/tmp/model_checkpoints',
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_dir='/tmp/logs',
        logging_steps=10,
        save_total_limit=2,
    )
    
    # Définir les métriques
    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = logits.argmax(axis=-1)
        acc = accuracy_score(labels, predictions)
        f1 = f1_score(labels, predictions, average='binary')
        return {'accuracy': acc, 'f1': f1}
    
    # Créer le Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )
    
    # Entraîner le modèle
    print(f"🏋️ Entraînement du modèle ({epochs} époques)...")
    train_result = trainer.train()
    
    # Évaluer le modèle
    print("📊 Évaluation du modèle...")
    eval_result = trainer.evaluate()
    
    print(f"✅ Résultats:")
    print(f"   - Accuracy: {eval_result['eval_accuracy']:.4f}")
    print(f"   - F1-Score: {eval_result['eval_f1']:.4f}")
    print(f"   - Loss: {eval_result['eval_loss']:.4f}")
    
    # Sauvegarder le modèle
    model_path = model_output.path
    print(f"💾 Sauvegarde du modèle dans {model_path}...")
    
    trainer.save_model(model_path)
    tokenizer.save_pretrained(model_path)
    
    # Sauvegarder les métadonnées
    metadata = {
        'model_name': model_name,
        'epochs': epochs,
        'learning_rate': learning_rate,
        'batch_size': batch_size,
        'accuracy': float(eval_result['eval_accuracy']),
        'f1_score': float(eval_result['eval_f1']),
        'num_train_samples': len(train_texts),
        'num_val_samples': len(val_texts)
    }
    
    with open(f"{model_path}/metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Logger les métriques dans Vertex AI
    metrics.log_metric('accuracy', eval_result['eval_accuracy'])
    metrics.log_metric('f1_score', eval_result['eval_f1'])
    metrics.log_metric('train_loss', train_result.training_loss)
    metrics.log_metric('eval_loss', eval_result['eval_loss'])
    
    print("✅ Entraînement terminé avec succès!")
