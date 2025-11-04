#!/usr/bin/env python3
"""
Script de déploiement Docker pour l'API Digital Social Score
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Exécute une commande et retourne le résultat"""
    print(f"🔧 Executing: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print("✅ Success")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print("❌ Failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_docker():
    """Vérifie que Docker est installé et en cours d'exécution"""
    print("🔍 Checking Docker...")
    if not run_command("docker --version"):
        print("❌ Docker n'est pas installé ou non accessible")
        return False
    
    if not run_command("docker info"):
        print("❌ Docker daemon n'est pas en cours d'exécution")
        return False
    
    return True

def build_image():
    """Construit l'image Docker"""
    print("🔨 Building Docker image...")
    return run_command("docker build -t digital-social-score-api .")

def run_container():
    """Lance le conteneur"""
    print("🚀 Starting container...")
    
    # Arrêter le conteneur s'il existe déjà
    run_command("docker stop digital-social-score-api")
    run_command("docker rm digital-social-score-api")
    
    # Lancer le nouveau conteneur
    command = """docker run -d \
        --name digital-social-score-api \
        -p 8000:8000 \
        -v "{models_path}:/app/models:ro" \
        --restart unless-stopped \
        digital-social-score-api""".format(
        models_path=str(Path("../etape2-modele-ia/models").resolve())
    )
    
    return run_command(command)

def wait_for_api():
    """Attend que l'API soit prête"""
    print("⏳ Waiting for API to be ready...")
    
    import requests
    for i in range(30):  # Attendre jusqu'à 30 secondes
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ API is ready!")
                return True
        except:
            pass
        
        time.sleep(1)
        print(f"   Attempt {i+1}/30...")
    
    print("❌ API failed to start in time")
    return False

def run_tests():
    """Lance les tests de validation"""
    print("🧪 Running validation tests...")
    return run_command("python validate_api.py")

def deploy_with_compose():
    """Déploie avec docker-compose"""
    print("🐳 Deploying with docker-compose...")
    
    # Arrêter les services existants
    run_command("docker-compose down")
    
    # Lancer les services
    if run_command("docker-compose up -d --build"):
        print("✅ Services started with docker-compose")
        return True
    return False

def show_status():
    """Affiche le statut du déploiement"""
    print("\n📊 DEPLOYMENT STATUS")
    print("=" * 40)
    
    # Statut du conteneur
    run_command("docker ps | grep digital-social-score")
    
    # Logs récents
    print("\n📝 Recent logs:")
    run_command("docker logs --tail 10 digital-social-score-api")
    
    print(f"\n🌐 API Endpoints:")
    print(f"   • Health: http://localhost:8000/health")
    print(f"   • Docs: http://localhost:8000/docs")
    print(f"   • API: http://localhost:8000/analyze")

def main():
    """Fonction principale de déploiement"""
    print("🚀 DIGITAL SOCIAL SCORE API - DOCKER DEPLOYMENT")
    print("=" * 50)
    
    # Vérifier les prérequis
    if not check_docker():
        return 1
    
    # Menu de choix
    print("\nChoose deployment method:")
    print("1. Docker build & run")
    print("2. Docker Compose")
    print("3. Run tests only")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        # Méthode 1: Build et run manuel
        if not build_image():
            return 1
        
        if not run_container():
            return 1
        
        if not wait_for_api():
            return 1
        
        if not run_tests():
            print("⚠️ Some tests failed, but API is running")
        
        show_status()
    
    elif choice == "2":
        # Méthode 2: Docker Compose
        if not deploy_with_compose():
            return 1
        
        if not wait_for_api():
            return 1
        
        if not run_tests():
            print("⚠️ Some tests failed, but API is running")
        
        show_status()
    
    elif choice == "3":
        # Tests seulement
        if not run_tests():
            return 1
    
    else:
        print("❌ Invalid choice")
        return 1
    
    print("\n🎉 Deployment completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
