#!/usr/bin/env python
"""
Test du port 4443 pour Capdrive
"""
import os
import requests
import socket
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_port_4443():
    """Test spécifique du port 4443"""
    print("🚀 Test du port 4443 pour Capdrive")
    print("=" * 50)
    
    # Test de connexion sur le port 4443
    print("🔌 Test de connexion TCP sur le port 4443...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('capdrive.caplogy.com', 4443))
        sock.close()
        if result == 0:
            print("✅ Connexion TCP réussie sur le port 4443")
        else:
            print(f"❌ Connexion TCP échouée: code {result}")
            return False
    except Exception as e:
        print(f"❌ Erreur TCP: {e}")
        return False
    
    # Test HTTPS sur le port 4443
    print("\n🌐 Test HTTPS sur le port 4443...")
    try:
        # Test avec verify=False pour ignorer le certificat SSL
        response = requests.get('https://capdrive.caplogy.com:4443', timeout=10, verify=False)
        print(f"✅ Réponse HTTPS: {response.status_code}")
        if response.status_code == 200:
            print("✅ Site accessible en HTTPS sur le port 4443")
        else:
            print(f"⚠️  Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur HTTPS: {e}")
        return False
    
    # Test WebDAV
    print("\n🔧 Test WebDAV sur le port 4443...")
    webdav_url = os.getenv('NEXTCLOUD_WEBDAV_URL')
    user = os.getenv('NEXTCLOUD_USER')
    password = os.getenv('NEXTCLOUD_PASSWORD')
    
    print(f"🎯 URL: {webdav_url}")
    print(f"👤 Utilisateur: {user}")
    
    try:
        response = requests.request(
            'PROPFIND',
            webdav_url,
            auth=(user, password),
            headers={'Depth': '0'},
            timeout=10,
            verify=False  # Ignorer le certificat SSL
        )
        print(f"✅ Réponse WebDAV: {response.status_code}")
        
        if response.status_code == 207:
            print("🎉 WebDAV fonctionne parfaitement!")
            return True
        elif response.status_code == 401:
            print("❌ Erreur d'authentification")
            print("   Vérifiez vos identifiants")
            return False
        elif response.status_code == 404:
            print("❌ Endpoint WebDAV non trouvé")
            print("   Vérifiez l'URL WebDAV")
            return False
        else:
            print(f"⚠️  Réponse inattendue: {response.status_code}")
            print(f"   Contenu: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Erreur WebDAV: {e}")
        return False

if __name__ == "__main__":
    if test_port_4443():
        print("\n✅ SUCCESS: Capdrive fonctionne sur le port 4443!")
        print("🎯 Votre configuration est maintenant correcte.")
        print("⚠️  Note: Le certificat SSL sera ignoré (verify=False)")
    else:
        print("\n❌ Il y a encore un problème à résoudre.")
