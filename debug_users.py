#!/usr/bin/env python
"""
Script pour lister les utilisateurs Moodle disponibles
"""

import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'caplogy_project.settings')
django.setup()

from caplogy_app.services.moodle_api import MoodleAPI
from caplogy_app.services.user_service import UserService

def list_moodle_users():
    """Liste tous les utilisateurs Moodle"""
    print("=== Utilisateurs Moodle disponibles ===")
    
    try:
        api = MoodleAPI(
            url=os.getenv('MOODLE_URL'),
            token=os.getenv('MOODLE_TOKEN')
        )
        
        # Récupérer tous les utilisateurs avec un critère large
        try:
            params = {'criteria[0][key]': 'id', 'criteria[0][value]': '1'}
            result = api._request('core_user_get_users', params)
            users = result.get('users', []) if isinstance(result, dict) else []
            
            if users:
                print(f"✅ Trouvé {len(users)} utilisateurs Moodle (échantillon):")
                for user in users[:10]:  # Afficher les 10 premiers
                    print(f"  - {user.get('username', 'N/A')} ({user.get('firstname', '')} {user.get('lastname', '')}) - {user.get('email', 'N/A')}")
            else:
                print("❌ Aucun utilisateur trouvé")
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des utilisateurs: {e}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la connexion à Moodle: {e}")

def list_ldap_profs():
    """Liste tous les professeurs LDAP"""
    print("\n=== Professeurs LDAP disponibles ===")
    
    try:
        user_service = UserService()
        profs = user_service.get_ldap_profs()
        
        if profs:
            print(f"✅ Trouvé {len(profs)} professeurs LDAP:")
            for prof in profs:
                print(f"  - {prof['username']} ({prof['name']}) - {prof['mail']}")
        else:
            print("❌ Aucun professeur LDAP trouvé")
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des professeurs LDAP: {e}")

def find_user_in_moodle(username):
    """Recherche un utilisateur spécifique dans Moodle"""
    print(f"\n=== Recherche de l'utilisateur '{username}' dans Moodle ===")
    
    try:
        api = MoodleAPI(
            url=os.getenv('MOODLE_URL'),
            token=os.getenv('MOODLE_TOKEN')
        )

        # Recherche par email
        try:
            email = f"{username}@caplogy.com"
            params = {'criteria[0][key]': 'email', 'criteria[0][value]': email}
            result = api._request('core_user_get_users', params)
            users = result.get('users', []) if isinstance(result, dict) else []
            if users:
                user = users[0]
                print(f"✅ Trouvé par email: {user}")
                return user
            else:
                print(f"❌ Email '{email}' non trouvé dans Moodle")
        except Exception as e:
            print(f"❌ Erreur lors de la recherche par email: {e}")

        # Recherche par idnumber
        try:
            params = {'criteria[0][key]': 'idnumber', 'criteria[0][value]': username}
            result = api._request('core_user_get_users', params)
            users = result.get('users', []) if isinstance(result, dict) else []
            if users:
                user = users[0]
                print(f"✅ Trouvé par idnumber: {user}")
                return user
            else:
                print(f"❌ idnumber '{username}' non trouvé dans Moodle")
        except Exception as e:
            print(f"❌ Erreur lors de la recherche par idnumber: {e}")

        print(f"❌ Utilisateur '{username}' non trouvé dans Moodle")
        return None

    except Exception as e:
        print(f"❌ Erreur lors de la recherche: {e}")
        return None

def main():
    """Fonction principale"""
    print("=== Analyse des utilisateurs Moodle et LDAP ===\n")
    
    # Lister les utilisateurs Moodle
    list_moodle_users()
    
    # Lister les professeurs LDAP
    list_ldap_profs()
    
    # Rechercher l'utilisateur spécifique
    find_user_in_moodle("s.dawaliby")
    
    print("\n=== Suggestions ===")
    print("1. Vérifiez si s.dawaliby a un compte Moodle avec un username différent")
    print("2. Créez un compte Moodle pour s.dawaliby si nécessaire")
    print("3. Vérifiez l'email s.dawaliby@caplogy.com dans Moodle")

if __name__ == "__main__":
    main()
