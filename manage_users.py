#!/usr/bin/env python
"""
Script de gestion des utilisateurs Django pour Caplogy
Usage: python manage_users.py [commande] [options]

Commandes disponibles:
- create: Créer un nouveau compte utilisateur
- list: Lister tous les utilisateurs
- update: Mettre à jour un utilisateur existant
- delete: Supprimer un utilisateur
- promote: Promouvoir un utilisateur en admin
- demote: Rétrograder un admin en utilisateur normal
"""

import os
import sys
import django
from django.core.management.base import BaseCommand

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'caplogy_project.settings')
django.setup()

from django.contrib.auth.models import User
from caplogy_app.models import UserProfile

class UserManager:
    def create_user(self, username, password=None, email=None, role='user'):
        """Créer un nouveau utilisateur avec son profil"""
        try:
            # Vérifier si l'utilisateur existe déjà
            if User.objects.filter(username=username).exists():
                print(f"❌ Erreur: L'utilisateur '{username}' existe déjà")
                return False
            
            # Créer l'utilisateur Django
            user = User.objects.create_user(
                username=username,
                password=password or 'changeme123',
                email=email or f"{username}@example.com"
            )
            
            # Créer le profil utilisateur
            UserProfile.objects.create(user=user, role=role)
            
            print(f"✅ Utilisateur '{username}' créé avec succès")
            print(f"   - Rôle: {role}")
            print(f"   - Email: {user.email}")
            if not password:
                print(f"   - Mot de passe par défaut: changeme123")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de l'utilisateur: {e}")
            return False
    
    def list_users(self):
        """Lister tous les utilisateurs"""
        users = User.objects.all()
        
        if not users:
            print("Aucun utilisateur trouvé")
            return
        
        print("\n📋 Liste des utilisateurs:")
        print("-" * 60)
        print(f"{'ID':<5} {'Nom d\'utilisateur':<20} {'Email':<25} {'Rôle':<10}")
        print("-" * 60)
        
        for user in users:
            profile = getattr(user, 'userprofile', None)
            role = profile.role if profile else 'none'
            print(f"{user.id:<5} {user.username:<20} {user.email:<25} {role:<10}")
    
    def update_user(self, username, role=None, email=None, password=None):
        """Mettre à jour un utilisateur existant"""
        try:
            user = User.objects.get(username=username)
            
            # Mettre à jour l'email si fourni
            if email:
                user.email = email
                user.save()
                print(f"✅ Email mis à jour: {email}")
            
            # Mettre à jour le mot de passe si fourni
            if password:
                user.set_password(password)
                user.save()
                print(f"✅ Mot de passe mis à jour")
            
            # Mettre à jour le rôle si fourni
            if role:
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.role = role
                profile.save()
                print(f"✅ Rôle mis à jour: {role}")
            
            print(f"✅ Utilisateur '{username}' mis à jour avec succès")
            return True
            
        except User.DoesNotExist:
            print(f"❌ Erreur: L'utilisateur '{username}' n'existe pas")
            return False
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour: {e}")
            return False
    
    def delete_user(self, username):
        """Supprimer un utilisateur"""
        try:
            user = User.objects.get(username=username)
            user.delete()
            print(f"✅ Utilisateur '{username}' supprimé avec succès")
            return True
            
        except User.DoesNotExist:
            print(f"❌ Erreur: L'utilisateur '{username}' n'existe pas")
            return False
        except Exception as e:
            print(f"❌ Erreur lors de la suppression: {e}")
            return False
    
    def promote_user(self, username):
        """Promouvoir un utilisateur en admin"""
        return self.update_user(username, role='admin')
    
    def demote_user(self, username):
        """Rétrograder un admin en utilisateur normal"""
        return self.update_user(username, role='user')

def main():
    manager = UserManager()
    
    if len(sys.argv) < 2:
        print("Usage: python manage_users.py [commande] [options]")
        print("\nCommandes disponibles:")
        print("  create <username> [password] [email] [role]")
        print("  list")
        print("  update <username> [--role=<role>] [--email=<email>] [--password=<password>]")
        print("  delete <username>")
        print("  promote <username>")
        print("  demote <username>")
        print("\nRôles disponibles: admin, user, none")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_users.py create <username> [password] [email] [role]")
            return
        
        username = sys.argv[2]
        password = sys.argv[3] if len(sys.argv) > 3 else None
        email = sys.argv[4] if len(sys.argv) > 4 else None
        role = sys.argv[5] if len(sys.argv) > 5 else 'user'
        
        manager.create_user(username, password, email, role)
    
    elif command == 'list':
        manager.list_users()
    
    elif command == 'update':
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_users.py update <username> [--role=<role>] [--email=<email>] [--password=<password>]")
            return
        
        username = sys.argv[2]
        role = None
        email = None
        password = None
        
        # Parser les arguments optionnels
        for arg in sys.argv[3:]:
            if arg.startswith('--role='):
                role = arg.split('=')[1]
            elif arg.startswith('--email='):
                email = arg.split('=')[1]
            elif arg.startswith('--password='):
                password = arg.split('=')[1]
        
        manager.update_user(username, role, email, password)
    
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_users.py delete <username>")
            return
        
        username = sys.argv[2]
        confirm = input(f"⚠️  Êtes-vous sûr de vouloir supprimer l'utilisateur '{username}' ? (oui/non): ")
        if confirm.lower() in ['oui', 'o', 'yes', 'y']:
            manager.delete_user(username)
        else:
            print("❌ Suppression annulée")
    
    elif command == 'promote':
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_users.py promote <username>")
            return
        
        username = sys.argv[2]
        manager.promote_user(username)
    
    elif command == 'demote':
        if len(sys.argv) < 3:
            print("❌ Usage: python manage_users.py demote <username>")
            return
        
        username = sys.argv[2]
        manager.demote_user(username)
    
    else:
        print(f"❌ Commande inconnue: {command}")
        print("Commandes disponibles: create, list, update, delete, promote, demote")

if __name__ == '__main__':
    main()
