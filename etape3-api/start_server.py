#!/usr/bin/env python3
"""
Script de démarrage pour l'API Digital Social Score
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire courant au path Python
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    try:
        print("🚀 Démarrage de l'API Digital Social Score...")
        
        # Import et démarrage de l'API
        from app.main import app
        import uvicorn
        
        print("✅ Modules importés avec succès")
        print("🌐 Démarrage du serveur sur http://localhost:8000")
        print("📖 Documentation: http://localhost:8000/docs")
        print("⚡ Santé: http://localhost:8000/health")
        print()
        print("Appuyez sur Ctrl+C pour arrêter le serveur")
        
        # Démarrer le serveur
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,  # Pas de reload en production
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
