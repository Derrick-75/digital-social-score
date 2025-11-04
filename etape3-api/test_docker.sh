#!/bin/bash
# Script de test Docker pour l'API Digital Social Score

echo "🐳 Test Docker - Digital Social Score API"
echo "=========================================="

# Vérifier que Docker fonctionne
echo "🔍 Vérification de Docker..."
docker --version
if [ $? -ne 0 ]; then
    echo "❌ Docker n'est pas démarré"
    echo "💡 Démarrez Docker Desktop et relancez ce script"
    exit 1
fi

echo "✅ Docker est disponible"

# Build de l'image
echo ""
echo "🏗️  Construction de l'image..."
docker build -t digital-social-score-api .

if [ $? -eq 0 ]; then
    echo "✅ Image construite avec succès"
else
    echo "❌ Erreur lors de la construction"
    exit 1
fi

# Lancement du container
echo ""
echo "🚀 Démarrage du container..."
echo "📖 API sera disponible sur http://localhost:8000"
echo "🛑 Appuyez sur Ctrl+C pour arrêter"

docker run -p 8000:8000 --name dss-api digital-social-score-api
