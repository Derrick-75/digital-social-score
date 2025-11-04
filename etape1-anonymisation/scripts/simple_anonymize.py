"""
Script d'anonymisation simplifié pour créer rapidement les données nécessaires
"""

import pandas as pd
import re
import os

def simple_anonymize_text(text):
    """Anonymisation simple basée sur des regex"""
    if pd.isna(text):
        return text
    
    # Patterns de base pour l'anonymisation
    patterns = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.]?)?(?:\(?[0-9]{3}\)?[-.]?)?[0-9]{3}[-.]?[0-9]{4}\b',
        'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        'credit_card': r'\b(?:[0-9]{4}[-\s]?){3}[0-9]{4}\b',
        'url': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    }
    
    replacements = {
        'email': '[EMAIL]',
        'phone': '[PHONE]',
        'ip_address': '[IP_ADDRESS]',
        'credit_card': '[CREDIT_CARD]',
        'url': '[URL]'
    }
    
    anonymized_text = str(text)
    
    # Appliquer les remplacements
    for pattern_name, pattern in patterns.items():
        anonymized_text = re.sub(pattern, replacements[pattern_name], anonymized_text)
    
    return anonymized_text

def main():
    print("🚀 Démarrage de l'anonymisation simplifiée...")
    
    # Chemins des données
    data_dir = "../data"
    raw_dir = os.path.join(data_dir, "raw")
    anonymized_dir = os.path.join(data_dir, "anonymized")
    
    # Créer le dossier de sortie
    os.makedirs(anonymized_dir, exist_ok=True)
    
    # Fichiers à traiter
    files = [
        ("train_advanced.csv", "train_anonymized.csv"),
        ("test_advanced.csv", "test_anonymized.csv")
    ]
    
    for input_file, output_file in files:
        input_path = os.path.join(raw_dir, input_file)
        output_path = os.path.join(anonymized_dir, output_file)
        
        print(f"\n📊 Traitement de {input_file}...")
        
        # Charger les données
        df = pd.read_csv(input_path)
        print(f"   Lignes: {len(df):,}")
        print(f"   Colonnes: {list(df.columns)}")
        
        # Anonymiser les colonnes de texte
        text_columns = ['comment_text']  # Ajuster selon la structure réelle
        
        for col in text_columns:
            if col in df.columns:
                print(f"   Anonymisation de la colonne: {col}")
                df[col] = df[col].apply(simple_anonymize_text)
        
        # Sauvegarder
        df.to_csv(output_path, index=False)
        print(f"✅ Sauvegardé: {output_path}")
    
    print("\n🎉 Anonymisation terminée avec succès!")

if __name__ == "__main__":
    main()
