import pandas as pd
from faker import Faker
import os

# Initialiser Faker
fake = Faker('en_US')  # Utilise la locale anglaise pour être cohérent avec les commentaires

# Construire les chemins vers les fichiers sources
current_dir = os.path.dirname(os.path.abspath(__file__))
raw_dir = os.path.join(current_dir, "raw")

# Liste des fichiers à enrichir
files_to_process = [
    {"input": "test.csv", "output": "test_advanced.csv"},
    {"input": "train.csv", "output": "train_advanced.csv"}
]

def enrich_dataframe(df):
    """Fonction pour enrichir un DataFrame avec des données fictives"""
    num_rows = len(df)
    print(f"📊 Enrichissement de {num_rows} lignes de données...")
    
    df["username"] = [fake.user_name() for _ in range(num_rows)]
    df["email"] = [fake.email() for _ in range(num_rows)]
    df["ip_address"] = [fake.ipv4() for _ in range(num_rows)]
    df["country"] = [fake.country() for _ in range(num_rows)]
    df["date_posted"] = [fake.date_time_this_year().strftime("%Y-%m-%d %H:%M:%S") for _ in range(num_rows)]
    df["phone_number"] = [fake.phone_number() for _ in range(num_rows)]
    df["company"] = [fake.company() for _ in range(num_rows)]
    df["user_agent"] = [fake.user_agent() for _ in range(num_rows)]
    df["device"] = [fake.android_platform_token() for _ in range(num_rows)]
    
    return df

# Traiter chaque fichier
for file_info in files_to_process:
    input_path = os.path.join(raw_dir, file_info["input"])
    output_path = os.path.join(raw_dir, file_info["output"])
    
    print(f"\n🔄 Traitement du fichier : {file_info['input']}")
    
    try:
        # Lire le fichier CSV
        df = pd.read_csv(input_path)
        
        # Enrichir le DataFrame
        df_enriched = enrich_dataframe(df)
        
        # Sauvegarder le fichier enrichi
        df_enriched.to_csv(output_path, index=False)
        
        print(f"✅ Fichier enrichi généré : {output_path}")
        print(f"📈 Nouvelles colonnes ajoutées : username, email, ip_address, country, date_posted, phone_number, company, user_agent, device")
        print(f"🔢 Nombre total de colonnes : {len(df_enriched.columns)}")
        print(f"📝 Premières lignes du dataset enrichi :")
        print(df_enriched.head(2))
        
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier {input_path} n'existe pas")
    except Exception as e:
        print(f"❌ Erreur lors du traitement de {file_info['input']} : {str(e)}")

print(f"\n🎉 Traitement terminé ! Tous les fichiers ont été enrichis.")