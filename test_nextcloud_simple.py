#!/usr/bin/env python3
"""
Test de diagnostic simple pour NextcloudAPI
"""

import os
import sys
import time
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le path pour importer les modules Django
sys.path.append('.')
sys.path.append('caplogy_app')

def test_nextcloud_connection():
    """Test de connexion Nextcloud étape par étape"""
    
    print("🔍 TEST NEXTCLOUD API")
    print("=" * 50)
    
    # 1. Vérifier les variables d'environnement
    print("📋 1. Variables d'environnement:")
    webdav_url = os.getenv('NEXTCLOUD_WEBDAV_URL')
    share_url = os.getenv('NEXTCLOUD_SHARE_URL')
    user = os.getenv('NEXTCLOUD_USER')
    password = os.getenv('NEXTCLOUD_PASSWORD')
    
    if not all([webdav_url, share_url, user, password]):
        print("❌ Variables manquantes!")
        return False
    
    print(f"✅ NEXTCLOUD_WEBDAV_URL: {webdav_url}")
    print(f"✅ NEXTCLOUD_USER: {user}")
    print(f"✅ NEXTCLOUD_PASSWORD: {'*' * len(password)}")
    
    # 2. Test de connectivité TCP
    print("\n🌐 2. Test connectivité TCP:")
    try:
        import socket
        from urllib.parse import urlparse
        
        parsed = urlparse(webdav_url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        
        sock = socket.create_connection((host, port), timeout=10)
        sock.close()
        print("✅ Connexion TCP réussie")
    except Exception as e:
        print(f"❌ Échec connexion TCP: {e}")
        return False
    
    # 3. Test HTTP de base
    print("\n🔗 3. Test HTTP de base:")
    try:
        import requests
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        print(f"   URL de base: {base_url}")
        response = requests.get(base_url, timeout=30, verify=False)
        print(f"✅ Réponse HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Échec HTTP: {e}")
        return False
    
    # 4. Test NextcloudAPI
    print("\n🔧 4. Test NextcloudAPI:")
    try:
        from caplogy_app.services.nextcloud_api import NextcloudAPI
        
        print("   Création de l'instance NextcloudAPI...")
        nc_api = NextcloudAPI(webdav_url, share_url, user, password)
        
        print("   Test du listing du répertoire racine...")
        print("   (Ceci peut prendre du temps, soyez patient...)")
        
        start_time = time.time()
        folders, files = nc_api.list_nc_dir('/')
        elapsed = time.time() - start_time
        
        print(f"✅ Test réussi en {elapsed:.2f}s")
        print(f"   Dossiers trouvés: {len(folders)}")
        print(f"   Fichiers trouvés: {len(files)}")
        
        if folders:
            print(f"   Premiers dossiers: {folders[:3]}")
        if files:
            print(f"   Premiers fichiers: {files[:3]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Échec NextcloudAPI: {e}")
        import traceback
        print(f"   Détails: {traceback.format_exc()}")
        return False

def main():
    success = test_nextcloud_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TOUS LES TESTS RÉUSSIS!")
        print("Votre NextcloudAPI est opérationnelle.")
    else:
        print("❌ ÉCHEC DES TESTS")
        print("Vérifiez votre configuration réseau et Nextcloud.")

if __name__ == "__main__":
    main()
