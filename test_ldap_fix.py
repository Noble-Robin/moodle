#!/usr/bin/env python
"""
Test rapide pour vérifier que la modification LDAP fonctionne
"""

import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'caplogy_project.settings')
django.setup()

from caplogy_app.services.user_service import UserService

# Test de connexion LDAP
def test_ldap_connection():
    print("=== Test de connexion LDAP ===")
    
    # Utilisation des identifiants qui fonctionnaient dans le test initial
    test_username = "t.frescaline"  # Identifiants qui fonctionnaient
    test_password = "&NC$U&QS*8cbiy"  # Mot de passe qui fonctionnait
    
    user_service = UserService()
    
    print(f"Test de connexion pour l'utilisateur: {test_username}")
    result = user_service.authenticate(test_username, test_password)
    
    if result:
        print(f"✅ Connexion réussie! Utilisateur: {result['username']}, Rôle: {result['role']}")
    else:
        print("❌ Échec de la connexion")
        
    return result is not None

if __name__ == "__main__":
    test_ldap_connection()
