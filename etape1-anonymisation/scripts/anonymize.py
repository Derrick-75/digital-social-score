"""
Script d'anonymisation des données pour le projet Digital Social Score
Conforme RGPD - Anonymisation irréversible des données personnelles
"""

import pandas as pd
import spacy
import re
import hashlib
import os
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class DataAnonymizer:
    """Classe pour l'anonymisation des données personnelles"""
    
    def __init__(self, spacy_model='en_core_web_lg'):
        """Initialise l'anonymiseur avec le modèle spaCy"""
        print(f"🚀 Chargement du modèle spaCy: {spacy_model}")
        self.nlp = spacy.load(spacy_model)
        
        # Entités à anonymiser
        self.sensitive_entities = ['PERSON', 'ORG', 'GPE', 'EMAIL', 'PHONE']
        
        # Patterns regex pour données personnelles
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.]?)?(?:\(?d{3}\)?[-.]?)?\d{3}[-.]?\d{4}\b',
            'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b'
        }
        
        # Mots de remplacement
        self.replacements = {
            'PERSON': '[PERSON]',
            'ORG': '[ORGANIZATION]', 
            'GPE': '[LOCATION]',
            'email': '[EMAIL]',
            'phone': '[PHONE]',
            'ip_address': '[IP_ADDRESS]',
            'credit_card': '[CREDIT_CARD]',
            'ssn': '[SSN]'
        }
        
        print("✅ Anonymiseur initialisé avec succès")
    
    def chunk_by_words(self, text: str, max_chars: int = 1000) -> List[str]:
        """Découpe le texte par mots sans casser les entités"""
        if len(text) <= max_chars:
            return [text]
        
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 pour l'espace
            
            # Si un seul mot dépasse la limite (URL très longue par exemple)
            if word_length > max_chars:
                # Finir le chunk actuel si nécessaire
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                # Traiter le mot long par caractères en dernier recours
                for i in range(0, len(word), max_chars):
                    chunks.append(word[i:i+max_chars])
                
            elif current_length + word_length > max_chars and current_chunk:
                # Finir le chunk actuel
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                # Ajouter le mot au chunk actuel
                current_chunk.append(word)
                current_length += word_length
        
        # Ajouter le dernier chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    def anonymize_with_ner(self, text: str) -> Tuple[str, Dict]:
        """Anonymise un texte en utilisant spaCy NER avec chunking par mots"""
        if not isinstance(text, str) or len(text.strip()) == 0:
            return text, {}
        
        try:
            # Utiliser chunking par mots pour les longs textes
            chunks = self.chunk_by_words(text, max_chars=1000)
            
            anonymized_chunks = []
            total_entities_found = {}
            
            for chunk in chunks:
                doc = self.nlp(chunk)
                anonymized_chunk = chunk
                
                # Remplacer les entités par ordre décroissant de position
                entities = sorted(doc.ents, key=lambda x: x.start_char, reverse=True)
                
                for ent in entities:
                    if ent.label_ in self.sensitive_entities:
                        replacement = self.replacements.get(ent.label_, f'[{ent.label_}]')
                        anonymized_chunk = (
                            anonymized_chunk[:ent.start_char] + 
                            replacement + 
                            anonymized_chunk[ent.end_char:]
                        )
                        
                        if ent.label_ not in total_entities_found:
                            total_entities_found[ent.label_] = 0
                        total_entities_found[ent.label_] += 1
                
                anonymized_chunks.append(anonymized_chunk)
            
            # Recoller tous les chunks
            final_text = " ".join(anonymized_chunks)
            return final_text, total_entities_found
            
        except Exception as e:
            print(f"⚠️ Erreur NER: {str(e)[:50]}")
            return text, {}
    
    def anonymize_with_patterns(self, text: str) -> Tuple[str, Dict]:
        """Anonymise un texte en utilisant des patterns regex"""
        if not isinstance(text, str):
            return text, {}
        
        anonymized_text = text
        patterns_found = {}
        
        for pattern_name, pattern in self.patterns.items():
            matches = re.findall(pattern, anonymized_text, re.IGNORECASE)
            if matches:
                patterns_found[pattern_name] = len(matches)
                replacement = self.replacements.get(pattern_name, f'[{pattern_name.upper()}]')
                anonymized_text = re.sub(pattern, replacement, anonymized_text, flags=re.IGNORECASE)
        
        return anonymized_text, patterns_found
    
    def anonymize_column(self, column_data: pd.Series, method='hash') -> pd.Series:
        """Anonymise une colonne de données personnelles"""
        if method == 'hash':
            # Hashage irréversible
            return column_data.astype(str).apply(
                lambda x: hashlib.sha256(x.encode()).hexdigest()[:8] if pd.notna(x) else x
            )
        elif method == 'mask':
            # Masquage simple
            return column_data.astype(str).apply(
                lambda x: '[MASKED]' if pd.notna(x) and x != 'nan' else x
            )
        else:
            return column_data
    
    def anonymize_dataframe(self, df: pd.DataFrame, save_stats=True) -> Tuple[pd.DataFrame, Dict]:
        """Anonymise un DataFrame complet"""
        df_anonymized = df.copy()
        stats = {
            'rows_processed': len(df),
            'columns_anonymized': [],
            'text_anonymization': {
                'ner_entities': {},
                'regex_patterns': {},
                'texts_modified': 0
            }
        }
        
        print(f"🔄 Anonymisation de {len(df)} lignes...")
        
        # 1. Anonymiser les colonnes de données personnelles directes
        personal_columns = {
            'username': 'hash',
            'email': 'hash', 
            'ip_address': 'hash',
            'phone_number': 'hash',
            'country': 'mask'  # Garder pour analyse géographique mais masquer
        }
        
        for col, method in personal_columns.items():
            if col in df_anonymized.columns:
                print(f"  📧 Anonymisation colonne: {col}")
                df_anonymized[col] = self.anonymize_column(df_anonymized[col], method)
                stats['columns_anonymized'].append(col)
        
        # 2. Anonymiser les textes avec NER et patterns
        if 'comment_text' in df_anonymized.columns:
            print("  📝 Anonymisation des commentaires...")
            
            for idx, text in enumerate(df_anonymized['comment_text']):
                if idx % 1000 == 0 and idx > 0:
                    print(f"    Progression: {idx}/{len(df_anonymized)}")
                
                # Appliquer NER
                anonymized_text, ner_entities = self.anonymize_with_ner(text)
                
                # Appliquer patterns regex
                anonymized_text, regex_patterns = self.anonymize_with_patterns(anonymized_text)
                
                # Mettre à jour le DataFrame
                if anonymized_text != text:
                    df_anonymized.loc[idx, 'comment_text'] = anonymized_text
                    stats['text_anonymization']['texts_modified'] += 1
                
                # Accumuler les statistiques
                for entity, count in ner_entities.items():
                    if entity not in stats['text_anonymization']['ner_entities']:
                        stats['text_anonymization']['ner_entities'][entity] = 0
                    stats['text_anonymization']['ner_entities'][entity] += count
                
                for pattern, count in regex_patterns.items():
                    if pattern not in stats['text_anonymization']['regex_patterns']:
                        stats['text_anonymization']['regex_patterns'][pattern] = 0
                    stats['text_anonymization']['regex_patterns'][pattern] += count
        
        print("✅ Anonymisation terminée")
        return df_anonymized, stats
    
    def save_anonymized_data(self, df: pd.DataFrame, output_path: str, stats: Dict):
        """Sauvegarde les données anonymisées et les statistiques"""
        # Sauvegarder le DataFrame
        df.to_csv(output_path, index=False)
        print(f"💾 Données anonymisées sauvegardées: {output_path}")
        
        # Sauvegarder les statistiques
        stats_path = output_path.replace('.csv', '_stats.txt')
        with open(stats_path, 'w', encoding='utf-8') as f:
            f.write("RAPPORT D'ANONYMISATION\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Lignes traitées: {stats['rows_processed']:,}\n")
            f.write(f"Colonnes anonymisées: {stats['columns_anonymized']}\n")
            f.write(f"Textes modifiés: {stats['text_anonymization']['texts_modified']}\n\n")
            
            f.write("ENTITÉS NER DÉTECTÉES:\n")
            for entity, count in stats['text_anonymization']['ner_entities'].items():
                f.write(f"  {entity}: {count}\n")
            
            f.write("\nPATTERNS REGEX DÉTECTÉS:\n")
            for pattern, count in stats['text_anonymization']['regex_patterns'].items():
                f.write(f"  {pattern}: {count}\n")
        
        print(f"📊 Statistiques sauvegardées: {stats_path}")

def main(max_rows=None):
    """Fonction principale d'anonymisation"""
    print("🛡️ DIGITAL SOCIAL SCORE - ANONYMISATION RGPD")
    print("=" * 60)
    
    if max_rows:
        print(f"🔢 MODE TEST: Limitation à {max_rows:,} lignes par fichier")
    
    # Chemins des fichiers
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', 'data')
    raw_dir = os.path.join(data_dir, 'raw')
    anonymized_dir = os.path.join(data_dir, 'anonymized')
    
    # Créer le dossier de sortie si nécessaire
    os.makedirs(anonymized_dir, exist_ok=True)
    
    # Fichiers à traiter
    files_to_process = [
        {'input': 'train_advanced.csv', 'output': 'train_anonymized.csv'},
        {'input': 'test_advanced.csv', 'output': 'test_anonymized.csv'}
    ]
    
    # Initialiser l'anonymiseur
    anonymizer = DataAnonymizer()
    
    # Traiter chaque fichier
    for file_info in files_to_process:
        input_path = os.path.join(raw_dir, file_info['input'])
        output_path = os.path.join(anonymized_dir, file_info['output'])
        
        print(f"\n📁 Traitement: {file_info['input']}")
        
        try:
            # Charger les données
            df = pd.read_csv(input_path)
            print(f"📊 Chargé: {df.shape[0]} lignes, {df.shape[1]} colonnes")
            
            # Limiter le nombre de lignes si spécifié
            if max_rows is not None:
                original_rows = len(df)
                df = df.head(max_rows)
                print(f"🔢 Dataset limité à {len(df)} lignes (sur {original_rows:,} au total)")
            
            # Anonymiser
            df_anonymized, stats = anonymizer.anonymize_dataframe(df)
            
            # Sauvegarder
            anonymizer.save_anonymized_data(df_anonymized, output_path, stats)
            
            # Afficher résumé
            print(f"✅ Fichier traité avec succès!")
            print(f"   📈 Colonnes anonymisées: {len(stats['columns_anonymized'])}")
            print(f"   📝 Textes modifiés: {stats['text_anonymization']['texts_modified']}")
            
        except FileNotFoundError:
            print(f"❌ Erreur: Fichier non trouvé {input_path}")
        except Exception as e:
            print(f"❌ Erreur lors du traitement: {str(e)}")
    
    print(f"\n🎉 ANONYMISATION TERMINÉE!")
    print(f"📁 Fichiers anonymisés disponibles dans: {anonymized_dir}")
    print(f"🛡️ Données conformes RGPD - Anonymisation irréversible")

if __name__ == "__main__":
    # Pour tester avec 20 000 lignes, décommentez la ligne suivante:
    # main(max_rows=20000)
    
    # Pour traiter tout le dataset:
    main()