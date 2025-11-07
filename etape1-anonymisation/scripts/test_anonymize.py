#!/usr/bin/env python3
"""
Script de test pour l'anonymisation - Limité à 20 000 lignes
"""

import sys
import os

# Ajouter le répertoire parent au path pour importer anonymize
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from anonymize import main

if __name__ == "__main__":
    print("🧪 TEST ANONYMISATION - 20 000 LIGNES")
    print("=" * 50)
    main(max_rows=20000)