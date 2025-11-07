#!/bin/bash
# Script d'installation des modèles spaCy requis

echo "🚀 Installation des modèles spaCy pour Digital Social Score"

# Modèles anglais (pour dataset Toxic Comment)
echo "📦 Installation du modèle anglais large..."
python -m spacy download en_core_web_lg

# Modèle français (pour commentaires français)
echo "📦 Installation du modèle français large..."
python -m spacy download fr_core_news_lg

# Modèle multilingue (backup)
echo "📦 Installation du modèle multilingue..."
python -m spacy download xx_ent_wiki_sm

echo "✅ Installation des modèles spaCy terminée !"
echo ""
echo "📋 Modèles installés :"
python -m spacy info en_core_web_lg
python -m spacy info fr_core_news_lg
python -m spacy info xx_ent_wiki_sm
