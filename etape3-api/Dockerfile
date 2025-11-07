# Dockerfile pour l'API Digital Social Score
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY app/ ./app/
# ❌ SUPPRIMÉ: COPY start_server.py .

# Créer un utilisateur non-root pour la sécurité
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Exposer le port
EXPOSE 8000

# Variables d'environnement
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO
ENV HOST=0.0.0.0
ENV PORT=8000

# ✅ CHANGÉ: Commande de démarrage avec uvicorn directement
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Métadonnées
LABEL maintainer="ESIGELEC - Digital Social Score Team"
LABEL version="1.0.0"
LABEL description="API de détection de toxicité - Conforme RGPD"