#!/usr/bin/env python
"""
Script pour créer automatiquement les utilisateurs Moodle à partir de LDAP
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

def create_moodle_user_from_ldap(username):
    """Crée un utilisateur Moodle à partir des informations LDAP"""
    print(f"=== Création automatique de l'utilisateur '{username}' dans Moodle ===")
    
    try:
        # Récupérer les informations LDAP
        user_service = UserService()
        ldap_profs = user_service.get_ldap_profs()
        
        # Trouver l'utilisateur dans LDAP
        ldap_user = None
        for prof in ldap_profs:
            if prof['username'] == username:
                ldap_user = prof
                break
        
        if not ldap_user:
            print(f"❌ Utilisateur '{username}' non trouvé dans LDAP")
            return False
        
        print(f"✅ Utilisateur trouvé dans LDAP: {ldap_user}")
        
        # Préparer les données pour Moodle
        api = MoodleAPI(
            url=os.getenv('MOODLE_URL'),
            token=os.getenv('MOODLE_TOKEN')
        )
        
        # Extraire le prénom et nom depuis le champ 'name'
        full_name = ldap_user['name']
        name_parts = full_name.split()
        
        # Logique pour extraire prénom et nom
        if len(name_parts) >= 2:
            # Prendre le premier mot comme prénom, le reste comme nom
            firstname = name_parts[0]
            lastname = ' '.join(name_parts[1:])
        else:
            firstname = full_name
            lastname = ''
        
        # Email par défaut si pas dans LDAP
        email = ldap_user.get('mail', f"{username}@caplogy.com")
        if not email or email == '[]':
            email = f"{username}@caplogy.com"
        
        # Données pour créer l'utilisateur Moodle
        user_data = {
            'users[0][username]': username,
            'users[0][firstname]': firstname,
            'users[0][lastname]': lastname,
            'users[0][email]': email,
            'users[0][password]': 'TempPass123!',  # Mot de passe temporaire
            'users[0][auth]': 'ldap',  # Authentification LDAP
            'users[0][idnumber]': username,
            'users[0][lang]': 'fr',
            'users[0][timezone]': 'Europe/Paris',
            'users[0][mailformat]': '1',
            'users[0][description]': f'Utilisateur créé automatiquement depuis LDAP: {full_name}',
            'users[0][city]': 'Paris',
            'users[0][country]': 'FR'
        }
        
        print(f"Création de l'utilisateur avec les données:")
        print(f"  - Username: {username}")
        print(f"  - Prénom: {firstname}")
        print(f"  - Nom: {lastname}")
        print(f"  - Email: {email}")
        
        # Créer l'utilisateur via l'API Moodle
        result = api._request('core_user_create_users', user_data)
        
        if result and isinstance(result, list) and len(result) > 0:
            user_id = result[0].get('id')
            print(f"✅ Utilisateur créé avec succès dans Moodle - ID: {user_id}")
            return True
        else:
            print(f"❌ Erreur lors de la création: {result}")
            return False
        
    except Exception as e:
        print(f"❌ Erreur lors de la création automatique: {e}")
        return False

def bulk_create_users_from_ldap():
    """Crée tous les utilisateurs LDAP manquants dans Moodle"""
    print("=== Création en masse des utilisateurs LDAP manquants ===")
    
    try:
        user_service = UserService()
        ldap_profs = user_service.get_ldap_profs()
        
        api = MoodleAPI(
            url=os.getenv('MOODLE_URL'),
            token=os.getenv('MOODLE_TOKEN')
        )
        
        created_count = 0
        failed_count = 0
        
        for prof in ldap_profs:
            username = prof['username']
            
            # Vérifier si l'utilisateur existe déjà dans Moodle
            try:
                params = {'field': 'username', 'values[0]': username}
                result = api._request('core_user_get_users_by_field', params)
                if isinstance(result, list) and result:
                    print(f"⏭️  Utilisateur '{username}' existe déjà dans Moodle")
                    continue
            except:
                pass
            
            # Créer l'utilisateur s'il n'existe pas
            if create_moodle_user_from_ldap(username):
                created_count += 1
            else:
                failed_count += 1
            
            print()  # Ligne vide pour la lisibilité
        
        print(f"=== Résumé ===")
        print(f"✅ Utilisateurs créés: {created_count}")
        print(f"❌ Échecs: {failed_count}")
        print(f"📊 Total traité: {len(ldap_profs)}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création en masse: {e}")

def main():
    """Fonction principale"""
    print("=== Création automatique d'utilisateurs Moodle depuis LDAP ===\n")
    
    # Option 1: Créer un utilisateur spécifique
    print("1. Création de s.dawaliby:")
    create_moodle_user_from_ldap("s.dawaliby")
    
    print("\n" + "="*50 + "\n")
    
    # Option 2: Demander si on veut créer tous les utilisateurs manquants
    response = input("Voulez-vous créer tous les utilisateurs LDAP manquants dans Moodle ? (y/N): ")
    if response.lower() in ['y', 'yes', 'oui']:
        bulk_create_users_from_ldap()

if __name__ == "__main__":
    main()
