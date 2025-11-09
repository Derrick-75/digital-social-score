"""
Composant Vertex AI : Préparation et anonymisation des données
Ce composant charge, nettoie et anonymise les données pour l'entraînement
"""

from kfp.dsl import component, Output, Dataset, Metrics
from typing import NamedTuple


@component(
    base_image="python:3.10-slim",
    packages_to_install=[
        "pandas==2.0.3",
        "spacy==3.7.2",
        "google-cloud-storage==2.10.0"
    ]
)
def prepare_data_op(
    raw_data_gcs_path: str,
    anonymized_data: Output[Dataset],
    metrics: Output[Metrics]
) -> NamedTuple('Outputs', [('num_samples', int), ('num_toxic', int)]):
    """
    Prépare et anonymise les données pour l'entraînement
    
    Args:
        raw_data_gcs_path: Chemin GCS vers les données brutes
        anonymized_data: Dataset de sortie avec données anonymisées
        metrics: Métriques de la préparation
    
    Returns:
        Nombre d'échantillons et nombre d'échantillons toxiques
    """
    import pandas as pd
    import spacy
    import hashlib
    import re
    import os
    from google.cloud import storage
    
    print("Chargement du modele spaCy pour NER...")
    # Telecharger et charger spaCy
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
    print(f"Modele charge: {nlp.meta['name']}")
    
    print(f"Chargement des donnees depuis {raw_data_gcs_path}...")
    
    # Charger les données depuis GCS
    client = storage.Client()
    bucket_name = raw_data_gcs_path.split('/')[2]
    blob_path = '/'.join(raw_data_gcs_path.split('/')[3:])
    
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    
    # Telecharger dans un fichier temporaire
    blob.download_to_filename('/tmp/raw_data.csv')
    df = pd.read_csv('/tmp/raw_data.csv')
    
    print(f"Charge {len(df)} lignes de donnees")
    
    def anonymize_text(text):
        """Anonymise les entites nommees dans le texte"""
        if pd.isna(text):
            return text
            
        doc = nlp(str(text))
        anonymized = text
        
        # Remplacer les entites par des hash
        for ent in reversed(doc.ents):
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'LOC']:
                hash_val = hashlib.sha256(ent.text.encode()).hexdigest()[:8]
                anonymized = anonymized[:ent.start_char] + f"[{ent.label_}_{hash_val}]" + anonymized[ent.end_char:]
        
        # Anonymiser les emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        anonymized = re.sub(email_pattern, '[EMAIL]', anonymized)
        
        return anonymized
    
    print("Anonymisation des textes...")
    df['text_anonymized'] = df['comment_text'].apply(anonymize_text)
    
    # Nettoyage basique
    df = df.dropna(subset=['text_anonymized'])
    df = df[df['text_anonymized'].str.len() > 10]
    
    # Statistiques
    num_samples = len(df)
    num_toxic = df['toxic'].sum() if 'toxic' in df.columns else 0
    
    print(f"Statistiques:")
    print(f"   - Total echantillons: {num_samples}")
    print(f"   - Echantillons toxiques: {num_toxic}")
    print(f"   - Taux de toxicite: {num_toxic/num_samples*100:.2f}%")
    
    # Sauvegarder les donnees anonymisees
    output_path = anonymized_data.path + '.csv'
    df.to_csv(output_path, index=False)
    
    # Logger les metriques
    metrics.log_metric('num_samples', num_samples)
    metrics.log_metric('num_toxic', num_toxic)
    metrics.log_metric('toxicity_rate', num_toxic/num_samples)
    
    print(f"Donnees anonymisees sauvegardees: {output_path}")
    
    from collections import namedtuple
    output = namedtuple('Outputs', ['num_samples', 'num_toxic'])
    return output(num_samples, num_toxic)
