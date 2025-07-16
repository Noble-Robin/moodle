#!/usr/bin/env python
"""
Script pour tester LDAP et créer un utilisateur admin
"""

import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'caplogy_project.settings')
django.setup()

from django.contrib.auth.models import User
from caplogy_app.models import UserProfile
from caplogy_app.services.user_service import UserService

def test_ldap_profs():
    """Test de récupération des professeurs LDAP"""
    print("=== Test de récupération des professeurs LDAP ===")
    
    user_service = UserService()
    profs = user_service.get_ldap_profs()
    
    if profs:
        print(f"✅ Récupération réussie! Trouvé {len(profs)} professeurs:")
        for prof in profs[:5]:  # Afficher les 5 premiers
            print(f"  - {prof['username']} ({prof['name']}) - {prof['mail']}")
        if len(profs) > 5:
            print(f"  ... et {len(profs) - 5} autres")
    else:
        print("❌ Échec de la récupération des professeurs")
    
    return len(profs) > 0

def create_admin_user():
    """Créer un utilisateur admin"""
    print("\n=== Création d'un utilisateur admin ===")
    
    username = 'r.noble'  # Remplace par ton nom d'utilisateur
    
    try:
        # Créer ou récupérer l'utilisateur Django
        user, created = User.objects.get_or_create(username=username)
        
        if created:
            print(f"✅ Utilisateur Django '{username}' créé")
        else:
            print(f"ℹ️  Utilisateur Django '{username}' existe déjà")
        
        # Créer ou récupérer le profil utilisateur
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'admin'}
        )
        
        if created:
            print(f"✅ Profil utilisateur créé avec le rôle 'admin'")
        else:
            # Mettre à jour le rôle s'il existe déjà
            if profile.role != 'admin':
                profile.role = 'admin'
                profile.save()
                print(f"✅ Rôle mis à jour vers 'admin'")
            else:
                print(f"ℹ️  L'utilisateur a déjà le rôle 'admin'")
        
        print(f"✅ Utilisateur '{username}' configuré comme admin")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur admin: {e}")
        return False

def main():
    """Fonction principale"""
    print("=== Script de test LDAP et création admin ===\n")
    
    # Test de récupération des professeurs LDAP
    test_ldap_profs()
    
    # Création d'un utilisateur admin
    create_admin_user()
    
    print("\n=== Fin du script ===")

if __name__ == "__main__":
    main()
