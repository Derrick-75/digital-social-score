# Étape 2 : Préparation et Entraînement d'un Modèle IA

## 🎯 Objectifs Pédagogiques

- Appréhender le nettoyage de texte et les modèles d'IA
- Entraîner et comparer un modèle simple et un modèle avancé (BERT)

## 📋 Exercices

### 1. Nettoyage des Textes
- [ ] Gestion de la ponctuation
- [ ] Traitement des emojis
- [ ] Normalisation de la casse
- [ ] Suppression des caractères spéciaux
- [ ] Tokenization

### 2. Entraînement Modèle Statistique
- [ ] Vectorisation TF-IDF ou Bag of Words
- [ ] Modèle de classification simple :
  - Logistic Regression
  - Naive Bayes
  - Random Forest
- [ ] Entraînement et validation

### 3. Entraînement Modèle Avancé
- [ ] Choix : LSTM ou BERT (recommandé)
- [ ] Utiliser HuggingFace Transformers
- [ ] Fine-tuning sur dataset toxicité
- [ ] Optimisation hyperparamètres

### 4. Comparaison des Modèles
- [ ] Métriques :
  - Précision (Precision)
  - Rappel (Recall)
  - F1-Score
  - AUC-ROC
  - Temps d'inférence
- [ ] Matrice de confusion
- [ ] Analyse des erreurs

## 🛠️ Technologies

```bash
pip install transformers torch scikit-learn pandas numpy nltk
```

## 📁 Structure

```
etape2-modele-ia/
├── notebooks/
│   ├── preprocessing.ipynb        # Nettoyage et préparation
│   ├── model_simple.ipynb         # Modèle statistique
│   └── model_bert.ipynb           # Modèle BERT
├── training/
│   ├── train_simple.py            # Entraînement modèle simple
│   ├── train_bert.py              # Entraînement BERT
│   └── utils.py                   # Fonctions utilitaires
├── evaluation/
│   ├── compare_models.py          # Comparaison performances
│   └── metrics.py                 # Calcul métriques
└── models/
    ├── simple_model.pkl           # Modèle simple sauvegardé
    └── bert_model/                # Modèle BERT sauvegardé
```

## 🧪 Pipeline de Traitement

```
Texte brut
    ↓
Nettoyage (ponctuation, emojis, casse)
    ↓
Tokenization
    ↓
┌──────────────────────┬──────────────────────┐
│  Modèle Statistique  │    Modèle BERT       │
│  (TF-IDF + LR)       │  (Transformers)      │
└──────────────────────┴──────────────────────┘
    ↓                           ↓
  Score 0-100              Score 0-100
```

## 📊 Livrables

- [ ] Scripts d'entraînement fonctionnels
- [ ] Modèles sauvegardés et exportés
- [ ] Rapport de comparaison détaillé :
  - Tableau comparatif des métriques
  - Graphiques de performance
  - Analyse temps de traitement
- [ ] Recommandation du meilleur modèle pour production

## ✅ Critères de Validation

- ✅ F1-Score > 0.75 pour le meilleur modèle
- ✅ Temps d'inférence < 500ms par texte
- ✅ Comparaison objective et documentée
- ✅ Modèle exporté et réutilisable

## 💡 Recommandations

### Modèle Simple (Baseline)
- **Avantages** : Rapide, léger, facile à déployer
- **Inconvénients** : Moins précis, ne comprend pas le contexte

### Modèle BERT
- **Avantages** : État de l'art, comprend le contexte
- **Inconvénients** : Lourd, nécessite GPU, plus lent

### Choix pour Production
Recommandation : Commencer avec BERT pour la précision, puis optimiser avec :
- Distillation de modèle (DistilBERT)
- Quantization
- ONNX Runtime

## 📚 Ressources

- [HuggingFace Transformers](https://huggingface.co/docs/transformers/index)
- [BERT Paper](https://arxiv.org/abs/1810.04805)
- [Scikit-learn Guide](https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html)
