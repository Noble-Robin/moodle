#!/usr/bin/env python
"""
Script de test pour vérifier la connexion à Capdrive
"""
import os
import sys
import requests
from xml.etree import ElementTree as ET
from urllib.parse import quote, unquote
import django
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'caplogy_project.settings')
django.setup()

from caplogy_app.services.nextcloud_api import NextcloudAPI

def test_capdrive_connection():
    """Test de base pour vérifier la connexion à Capdrive"""
    print("🔍 Test de connexion à Capdrive...")
    print("=" * 50)
    
    # Récupérer la configuration
    webdav_url = os.getenv('NEXTCLOUD_WEBDAV_URL')
    share_url = os.getenv('NEXTCLOUD_SHARE_URL')
    user = os.getenv('NEXTCLOUD_USER')
    password = os.getenv('NEXTCLOUD_PASSWORD')
    
    print(f"📋 Configuration:")
    print(f"  - WebDAV URL: {webdav_url}")
    print(f"  - Share URL: {share_url}")
    print(f"  - Utilisateur: {user}")
    print(f"  - Mot de passe: {'*' * len(password) if password else 'Non défini'}")
    print()
    
    if not all([webdav_url, share_url, user, password]):
        print("❌ Configuration incomplète dans le fichier .env")
        return False
    
    # Test 1: Créer l'instance API
    print("🔧 Test 1: Création de l'instance NextcloudAPI...")
    try:
        nc_api = NextcloudAPI(
            base_url=webdav_url,
            share_url=share_url,
            user=user,
            password=password
        )
        print("✅ Instance NextcloudAPI créée avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'instance: {e}")
        return False
    
    # Test 2: Test de connexion WebDAV basique
    print("\n🌐 Test 2: Connexion WebDAV de base...")
    try:
        # Test simple avec une requête PROPFIND sur la racine
        response = requests.request(
            'PROPFIND',
            webdav_url,
            auth=(user, password),
            headers={'Depth': '0'},
            verify=False,
            timeout=10
        )
        print(f"  - Status code: {response.status_code}")
        if response.status_code == 207:
            print("✅ Connexion WebDAV réussie")
        elif response.status_code == 401:
            print("❌ Erreur d'authentification (401)")
            return False
        else:
            print(f"⚠️  Réponse inattendue: {response.status_code}")
            print(f"  - Contenu: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Erreur de connexion WebDAV: {e}")
        return False
    
    # Test 3: Lister le répertoire racine
    print("\n📁 Test 3: Listage du répertoire racine...")
    try:
        folders, files = nc_api.list_nc_dir('/')
        print(f"✅ Répertoire listé avec succès:")
        print(f"  - {len(folders)} dossiers trouvés: {folders[:5]}{'...' if len(folders) > 5 else ''}")
        print(f"  - {len(files)} fichiers trouvés: {files[:5]}{'...' if len(files) > 5 else ''}")
    except Exception as e:
        print(f"❌ Erreur lors du listage: {e}")
        return False
    
    # Test 4: Lister un répertoire spécifique (si il existe)
    print("\n📂 Test 4: Listage d'un répertoire spécifique...")
    test_dirs = ['/Cours Test', '/Shared', '/Documents']
    
    for test_dir in test_dirs:
        try:
            print(f"  - Test du répertoire: {test_dir}")
            folders, files = nc_api.list_nc_dir(test_dir)
            print(f"    ✅ {len(folders)} dossiers, {len(files)} fichiers")
            break
        except Exception as e:
            print(f"    ⚠️  Répertoire non accessible: {e}")
    
    # Test 5: Test de l'API de partage (sans créer de partage)
    print("\n🔗 Test 5: Test de l'endpoint de partage...")
    try:
        # Test simple pour vérifier que l'endpoint répond
        response = requests.get(
            share_url,
            auth=(user, password),
            headers={'OCS-APIRequest': 'true'},
            verify=False,
            timeout=10
        )
        print(f"  - Status code: {response.status_code}")
        if response.status_code in [200, 400, 405]:  # 400/405 sont normaux sans paramètres
            print("✅ Endpoint de partage accessible")
        else:
            print(f"⚠️  Réponse inattendue: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur lors du test de l'API de partage: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés avec succès!")
    print("🎉 Votre configuration Capdrive semble fonctionnelle!")
    return True

def test_specific_directory():
    """Test pour un répertoire spécifique"""
    print("\n🎯 Test avancé: Répertoire spécifique")
    print("=" * 50)
    
    # Demander à l'utilisateur quel répertoire tester
    print("Répertoires suggérés à tester:")
    print("1. /Cours Test")
    print("2. /Shared/Biblio_Cours_Caplogy")
    print("3. /Documents")
    print("4. Autre (à saisir)")
    
    choice = input("\nChoisissez un répertoire (1-4): ").strip()
    
    if choice == "1":
        test_path = "/Cours Test"
    elif choice == "2":
        test_path = "/Shared/Biblio_Cours_Caplogy"
    elif choice == "3":
        test_path = "/Documents"
    elif choice == "4":
        test_path = input("Entrez le chemin du répertoire: ").strip()
    else:
        print("❌ Choix invalide")
        return
    
    print(f"\n🔍 Test du répertoire: {test_path}")
    
    try:
        nc_api = NextcloudAPI(
            base_url=os.getenv('NEXTCLOUD_WEBDAV_URL'),
            share_url=os.getenv('NEXTCLOUD_SHARE_URL'),
            user=os.getenv('NEXTCLOUD_USER'),
            password=os.getenv('NEXTCLOUD_PASSWORD')
        )
        
        folders, files = nc_api.list_nc_dir(test_path)
        
        print(f"✅ Contenu du répertoire '{test_path}':")
        print(f"\n📁 Dossiers ({len(folders)}):")
        for i, folder in enumerate(folders[:10], 1):
            print(f"  {i}. {folder}")
        if len(folders) > 10:
            print(f"  ... et {len(folders) - 10} autres dossiers")
        
        print(f"\n📄 Fichiers ({len(files)}):")
        for i, file in enumerate(files[:10], 1):
            print(f"  {i}. {file}")
        if len(files) > 10:
            print(f"  ... et {len(files) - 10} autres fichiers")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    print("🚀 Script de test Capdrive")
    print("=" * 50)
    
    # Test principal
    if test_capdrive_connection():
        # Proposer un test avancé
        response = input("\n🔧 Voulez-vous tester un répertoire spécifique? (o/n): ").lower().strip()
        if response in ['o', 'oui', 'y', 'yes']:
            test_specific_directory()
    
    print("\n👋 Fin des tests")
