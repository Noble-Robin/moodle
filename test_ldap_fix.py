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
    
    # Remplacez ces valeurs par des identifiants de test valides
    test_username = "r.noble"  # Changez selon votre environnement
    test_password = "votre_mot_de_passe"  # Changez selon votre environnement
    
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
