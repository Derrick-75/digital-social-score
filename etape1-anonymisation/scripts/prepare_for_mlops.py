"""
Script pour préparer les données pour le pipeline MLOps
Extrait seulement les colonnes nécessaires : comment_text et toxic
"""

import pandas as pd
import os

print("=" * 60)
print("📋 PRÉPARATION DES DONNÉES POUR MLOPS")
print("=" * 60)
print()

# Chemins des fichiers
input_dir = "../data/raw"
output_dir = "../data/mlops"

# Créer le dossier de sortie
os.makedirs(output_dir, exist_ok=True)

# Fichiers à traiter
files = [
    ("train_advanced.csv", "train.csv"),
    ("test_advanced.csv", "test.csv")
]

for input_file, output_file in files:
    input_path = os.path.join(input_dir, input_file)
    output_path = os.path.join(output_dir, output_file)
    
    print(f"📁 Traitement: {input_file}")
    
    # Charger les données
    df = pd.read_csv(input_path)
    print(f"   ✅ Chargé: {len(df):,} lignes, {len(df.columns)} colonnes")
    
    # Garder seulement les colonnes nécessaires
    # Le fichier test peut ne pas avoir la colonne 'toxic'
    if 'toxic' in df.columns:
        df_simple = df[['comment_text', 'toxic']].copy()
    else:
        print(f"   ⚠️  Pas de colonne 'toxic' - fichier de test")
        df_simple = df[['comment_text']].copy()
        # Ajouter une colonne toxic avec des 0 par défaut pour le test
        df_simple['toxic'] = 0
    
    # Nettoyer les données vides
    df_simple = df_simple.dropna(subset=['comment_text'])
    df_simple = df_simple[df_simple['comment_text'].str.len() > 0]
    
    # Sauvegarder
    df_simple.to_csv(output_path, index=False)
    
    file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
    print(f"   💾 Sauvegardé: {output_path}")
    print(f"   📊 {len(df_simple):,} lignes, {file_size:.2f} MB")
    if 'toxic' in df.columns:
        print(f"   📈 Taux de toxicité: {df_simple['toxic'].mean()*100:.2f}%")
    print()

print("=" * 60)
print("✅ DONNÉES PRÊTES POUR MLOPS!")
print("=" * 60)
print()
print(f"📁 Fichiers créés dans: {os.path.abspath(output_dir)}")
print()
print("🚀 Prochaines étapes:")
print("   1. Upload vers GCS:")
print("      cd ../etape7-mlops")
print("      python upload_data_to_gcs.py --project-id digitalsocialscoreapi \\")
print(f"        --train-file {os.path.abspath(os.path.join(output_dir, 'train.csv'))} \\")
print(f"        --test-file {os.path.abspath(os.path.join(output_dir, 'test.csv'))}")
print()
print("   2. Le pipeline MLOps fera l'anonymisation automatiquement!")
print()
