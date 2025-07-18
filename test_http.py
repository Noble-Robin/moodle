#!/usr/bin/env python
"""
Test rapide HTTP pour Capdrive
"""
import os
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_http_capdrive():
    """Test rapide en HTTP"""
    print("🚀 Test rapide Capdrive en HTTP")
    print("=" * 50)
    
    # Configuration
    webdav_url = os.getenv('NEXTCLOUD_WEBDAV_URL')
    user = os.getenv('NEXTCLOUD_USER')
    password = os.getenv('NEXTCLOUD_PASSWORD')
    
    print(f"🎯 URL: {webdav_url}")
    print(f"👤 Utilisateur: {user}")
    
    # Test HTTP simple
    print("\n🌐 Test HTTP basique...")
    try:
        response = requests.get('http://capdrive.caplogy.com', timeout=10)
        print(f"✅ Réponse HTTP: {response.status_code}")
        if response.status_code == 200:
            print("✅ Site accessible en HTTP")
        else:
            print(f"⚠️  Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur HTTP: {e}")
        return False
    
    # Test WebDAV
    print("\n🔧 Test WebDAV en HTTP...")
    try:
        response = requests.request(
            'PROPFIND',
            webdav_url,
            auth=(user, password),
            headers={'Depth': '0'},
            timeout=10
        )
        print(f"✅ Réponse WebDAV: {response.status_code}")
        
        if response.status_code == 207:
            print("🎉 WebDAV fonctionne parfaitement!")
            return True
        elif response.status_code == 401:
            print("❌ Erreur d'authentification")
            return False
        elif response.status_code == 404:
            print("❌ Endpoint WebDAV non trouvé")
            return False
        else:
            print(f"⚠️  Réponse inattendue: {response.status_code}")
            print(f"   Contenu: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Erreur WebDAV: {e}")
        return False

if __name__ == "__main__":
    if test_http_capdrive():
        print("\n✅ SUCCESS: Capdrive fonctionne maintenant!")
        print("🎯 Vous pouvez maintenant tester votre application Django.")
    else:
        print("\n❌ Il y a encore un problème à résoudre.")
