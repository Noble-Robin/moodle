#!/usr/bin/env python
"""
Script pour créer automatiquement les comptes Moodle pour les utilisateurs LDAP
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

def create_moodle_user_from_ldap(username, ldap_info):
    """Crée un utilisateur Moodle à partir des informations LDAP"""
    try:
        api = MoodleAPI(
            url=os.getenv('MOODLE_URL'),
            token=os.getenv('MOODLE_TOKEN')
        )
        
        # Préparer les données utilisateur
        user_data = {
            'username': username,
            'email': ldap_info.get('mail', f"{username}@caplogy.com"),
            'firstname': ldap_info.get('name', '').split(' ')[0] if ldap_info.get('name') else username,
            'lastname': ' '.join(ldap_info.get('name', '').split(' ')[1:]) if ldap_info.get('name') else '',
            'password': 'TempPass123!',  # Mot de passe temporaire
            'auth': 'ldap'  # Authentification LDAP
        }
        
        # Créer l'utilisateur via l'API Moodle
        params = {
            'users[0][username]': user_data['username'],
            'users[0][password]': user_data['password'],
            'users[0][firstname]': user_data['firstname'],
            'users[0][lastname]': user_data['lastname'],
            'users[0][email]': user_data['email'],
            'users[0][auth]': user_data['auth']
        }
        
        result = api._request('core_user_create_users', params)
        
        if result and isinstance(result, list) and result:
            user_id = result[0].get('id')
            print(f"✅ Utilisateur Moodle créé: {username} (ID: {user_id})")
            return user_id
        else:
            print(f"❌ Échec de la création de l'utilisateur: {username}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur {username}: {e}")
        return None

def sync_ldap_users_to_moodle():
    """Synchronise les utilisateurs LDAP vers Moodle"""
    print("=== Synchronisation des utilisateurs LDAP vers Moodle ===\n")
    
    try:
        # Récupérer les professeurs LDAP
        user_service = UserService()
        ldap_profs = user_service.get_ldap_profs()
        
        if not ldap_profs:
            print("❌ Aucun professeur LDAP trouvé")
            return
        
        print(f"✅ Trouvé {len(ldap_profs)} professeurs LDAP")
        
        # Créer les comptes Moodle manquants
        created_count = 0
        failed_count = 0
        
        for prof in ldap_profs:
            username = prof['username']
            print(f"\n--- Traitement de {username} ---")
            
            # Vérifier si l'utilisateur existe déjà dans Moodle
            try:
                api = MoodleAPI(
                    url=os.getenv('MOODLE_URL'),
                    token=os.getenv('MOODLE_TOKEN')
                )
                
                params = {'field': 'username', 'values[0]': username}
                result = api._request('core_user_get_users_by_field', params)
                
                if isinstance(result, list) and result:
                    print(f"ℹ️  Utilisateur {username} existe déjà dans Moodle")
                    continue
                    
            except Exception as e:
                print(f"❌ Erreur lors de la vérification de {username}: {e}")
                continue
            
            # Créer l'utilisateur Moodle
            user_id = create_moodle_user_from_ldap(username, prof)
            if user_id:
                created_count += 1
            else:
                failed_count += 1
        
        print(f"\n=== Résumé de la synchronisation ===")
        print(f"✅ Utilisateurs créés: {created_count}")
        print(f"❌ Échecs: {failed_count}")
        print(f"📊 Total traité: {len(ldap_profs)}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation: {e}")

def create_specific_user(username):
    """Crée un utilisateur spécifique à partir de LDAP"""
    print(f"=== Création de l'utilisateur {username} ===\n")
    
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
            print(f"❌ Utilisateur {username} non trouvé dans LDAP")
            return False
        
        print(f"✅ Utilisateur trouvé dans LDAP: {ldap_user}")
        
        # Créer l'utilisateur Moodle
        user_id = create_moodle_user_from_ldap(username, ldap_user)
        return user_id is not None
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de {username}: {e}")
        return False

def main():
    """Fonction principale"""
    print("=== Gestionnaire de synchronisation LDAP → Moodle ===\n")
    
    # Créer l'utilisateur spécifique s.dawaliby
    if create_specific_user("s.dawaliby"):
        print(f"\n✅ L'utilisateur s.dawaliby est maintenant disponible dans Moodle")
        print(f"🔄 Vous pouvez maintenant l'affecter aux cours")
    else:
        print(f"\n❌ Impossible de créer l'utilisateur s.dawaliby")
    
    # Optionnel : synchroniser tous les utilisateurs LDAP
    print(f"\n" + "="*50)
    response = input("Voulez-vous synchroniser tous les utilisateurs LDAP ? (y/N): ")
    if response.lower() == 'y':
        sync_ldap_users_to_moodle()

if __name__ == "__main__":
    main()
