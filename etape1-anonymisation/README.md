# Étape 1 : Exploration, Analyse et Anonymisation des Données

## 🎯 Objectifs Pédagogiques

- Repérer et traiter les données personnelles dans des textes
- Comprendre le cadre RGPD
- Mettre en œuvre l'anonymisation et la pseudonymisation

## 📋 Exercices

### 1. Téléchargement du Dataset
- [ ] Choisir dataset : [Toxic Comment Classification](https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge) ou [GameTox](https://github.com/hwang-su/gametox)
- [ ] Télécharger et placer dans `data/raw/`
- [ ] Explorer les données (statistiques, exemples)

### 2. Identification des Données Personnelles
- [ ] Identifier les types de données personnelles présentes :
  - Noms de personnes
  - Emails
  - Numéros de téléphone
  - Adresses
  - Identifiants
- [ ] Documenter les risques RGPD

### 3. Implémentation NER avec spaCy
- [ ] Installer spaCy et modèle français : `fr_core_news_lg`
- [ ] Créer script d'anonymisation
- [ ] Implémenter la détection et le masquage

### 4. Anonymisation et Comparaison
- [ ] Appliquer l'anonymisation sur le dataset
- [ ] Sauvegarder version anonymisée dans `data/anonymized/`
- [ ] Comparer :
  - Exemples avant/après
  - Statistiques (% de modifications)
  - Qualité de l'anonymisation

### 5. Documentation RGPD
- [ ] Remplir le registre de traitement (voir `docs/registre-rgpd.md`)
- [ ] Justifier chaque choix d'anonymisation
- [ ] Documenter la base légale du traitement

## 🛠️ Technologies

```bash
pip install spacy pandas numpy
python -m spacy download fr_core_news_lg
python -m spacy download en_core_web_lg
```

## 📁 Structure

```
etape1-anonymisation/
├── notebooks/
│   └── exploration.ipynb          # Analyse exploratoire
├── scripts/
│   ├── anonymize.py               # Script principal d'anonymisation
│   ├── ner_utils.py               # Fonctions utilitaires NER
│   └── compare.py                 # Comparaison avant/après
└── data/
    ├── raw/                       # Données brutes (gitignore)
    └── anonymized/                # Données anonymisées (gitignore)
```

## 📊 Livrables

- [ ] Script `anonymize.py` fonctionnel
- [ ] Notebook `exploration.ipynb` avec analyses
- [ ] Rapport de comparaison avant/après
- [ ] Section du registre RGPD complétée

## ✅ Critères de Validation

- ✅ 95%+ des données personnelles identifiées
- ✅ Anonymisation irréversible (pas de reversibilité)
- ✅ Préservation du sens des textes
- ✅ Documentation RGPD conforme

## 📚 Ressources

- [spaCy NER Guide](https://spacy.io/usage/linguistic-features#named-entities)
- [CNIL - Anonymisation](https://www.cnil.fr/fr/lanonymisation-de-donnees-un-traitement-cle-pour-lopen-data)
- [Guide RGPD](https://www.cnil.fr/fr/reglement-europeen-protection-donnees)
