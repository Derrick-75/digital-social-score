"""
Composant Vertex AI : Évaluation du modèle et décision de déploiement
Compare le nouveau modèle avec le modèle actuel en production
"""

from kfp.v2.dsl import component, Input, Output, Model, Dataset, Metrics
from typing import NamedTuple


@component(
    base_image="python:3.10-slim",
    packages_to_install=[
        "pandas==2.0.3",
        "scikit-learn==1.3.0",
        "transformers==4.35.0",
        "torch==2.1.0"
    ]
)
def evaluate_and_decide_op(
    test_data: Input[Dataset],
    new_model: Input[Model],
    current_model_f1: float,  # F1-Score du modèle actuel en production
    metrics: Output[Metrics],
    improvement_threshold: float = 0.02  # Amélioration minimale de 2%
) -> NamedTuple('Outputs', [('should_deploy', bool), ('new_f1_score', float)]):
    """
    Évalue le nouveau modèle et décide s'il doit remplacer l'ancien
    
    Args:
        test_data: Dataset de test
        new_model: Nouveau modèle entraîné
        current_model_f1: F1-Score du modèle actuellement en production
        metrics: Métriques d'évaluation
        improvement_threshold: Amélioration minimale requise pour déployer
    
    Returns:
        Décision de déploiement et nouveau F1-Score
    """
    import pandas as pd
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    from sklearn.metrics import (
        accuracy_score, 
        f1_score, 
        precision_score, 
        recall_score,
        confusion_matrix,
        classification_report
    )
    import json
    
    print("📊 Évaluation du nouveau modèle...")
    
    # Charger les données de test
    test_path = test_data.path + '.csv'
    df = pd.read_csv(test_path)
    
    test_texts = df['text_anonymized'].tolist()
    test_labels = df['toxic'].tolist()
    
    print(f"🧪 Dataset de test: {len(test_texts)} échantillons")
    
    # Charger le nouveau modèle
    model_path = new_model.path
    print(f"📥 Chargement du nouveau modèle depuis {model_path}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.eval()
    
    # Faire les prédictions
    print("🔮 Prédictions en cours...")
    predictions = []
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    
    batch_size = 16
    for i in range(0, len(test_texts), batch_size):
        batch_texts = test_texts[i:i+batch_size]
        
        inputs = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(device)
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            batch_predictions = torch.argmax(logits, dim=-1).cpu().numpy()
            predictions.extend(batch_predictions)
    
    # Calculer les métriques
    print("📈 Calcul des métriques...")
    
    accuracy = accuracy_score(test_labels, predictions)
    f1 = f1_score(test_labels, predictions, average='binary')
    precision = precision_score(test_labels, predictions, average='binary')
    recall = recall_score(test_labels, predictions, average='binary')
    
    cm = confusion_matrix(test_labels, predictions)
    
    print(f"\n📊 Résultats d'évaluation:")
    print(f"   Accuracy:  {accuracy:.4f}")
    print(f"   F1-Score:  {f1:.4f}")
    print(f"   Precision: {precision:.4f}")
    print(f"   Recall:    {recall:.4f}")
    print(f"\n   Confusion Matrix:")
    print(f"   {cm}")
    
    # Rapport détaillé
    report = classification_report(
        test_labels, 
        predictions, 
        target_names=['Non-toxic', 'Toxic']
    )
    print(f"\n{report}")
    
    # Décision de déploiement
    improvement = f1 - current_model_f1
    improvement_pct = improvement / current_model_f1 * 100
    
    should_deploy = improvement >= improvement_threshold
    
    print(f"\n🎯 DÉCISION DE DÉPLOIEMENT:")
    print(f"   F1-Score actuel:  {current_model_f1:.4f}")
    print(f"   F1-Score nouveau: {f1:.4f}")
    print(f"   Amélioration:     {improvement:.4f} ({improvement_pct:+.2f}%)")
    print(f"   Seuil requis:     {improvement_threshold:.4f}")
    
    if should_deploy:
        print(f"   ✅ DÉPLOYER - Amélioration significative détectée!")
    else:
        print(f"   ❌ NE PAS DÉPLOYER - Amélioration insuffisante")
    
    # Logger les métriques
    metrics.log_metric('new_accuracy', accuracy)
    metrics.log_metric('new_f1_score', f1)
    metrics.log_metric('new_precision', precision)
    metrics.log_metric('new_recall', recall)
    metrics.log_metric('current_f1_score', current_model_f1)
    metrics.log_metric('improvement', improvement)
    metrics.log_metric('improvement_pct', improvement_pct)
    metrics.log_metric('should_deploy', 1.0 if should_deploy else 0.0)
    
    # Sauvegarder le rapport d'évaluation
    evaluation_report = {
        'accuracy': float(accuracy),
        'f1_score': float(f1),
        'precision': float(precision),
        'recall': float(recall),
        'current_f1': float(current_model_f1),
        'improvement': float(improvement),
        'improvement_pct': float(improvement_pct),
        'should_deploy': bool(should_deploy),
        'confusion_matrix': cm.tolist(),
        'classification_report': report
    }
    
    with open(f"{model_path}/evaluation_report.json", 'w') as f:
        json.dump(evaluation_report, f, indent=2)
    
    print("✅ Évaluation terminée!")
    
    from collections import namedtuple
    output = namedtuple('Outputs', ['should_deploy', 'new_f1_score'])
    return output(should_deploy, f1)
