#!/usr/bin/env python
"""
Script de diagnostic simple pour Capdrive
"""
import os
import requests
import socket
from urllib.parse import urlparse
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_network_connectivity():
    """Test de connectivité réseau de base"""
    print("🌐 Test de connectivité réseau...")
    print("=" * 50)
    
    # Test 1: Résolution DNS
    print("📡 Test 1: Résolution DNS...")
    try:
        ip = socket.gethostbyname('capdrive.caplogy.com')
        print(f"✅ DNS résolu: capdrive.caplogy.com -> {ip}")
    except Exception as e:
        print(f"❌ Erreur DNS: {e}")
        return False
    
    # Test 2: Connexion TCP
    print("\n🔌 Test 2: Connexion TCP...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('capdrive.caplogy.com', 443))
        sock.close()
        if result == 0:
            print("✅ Connexion TCP réussie sur le port 443")
        else:
            print(f"❌ Connexion TCP échouée: code {result}")
            return False
    except Exception as e:
        print(f"❌ Erreur TCP: {e}")
        return False
    
    # Test 3: Test HTTP simple
    print("\n🌍 Test 3: Test HTTP simple...")
    try:
        response = requests.get('https://capdrive.caplogy.com', timeout=10, verify=False)
        print(f"✅ Réponse HTTP: {response.status_code}")
        if response.status_code == 200:
            print("✅ Site web accessible")
        else:
            print(f"⚠️  Status code: {response.status_code}")
    except requests.exceptions.Timeout:
        print("❌ Timeout lors de la requête HTTP")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Erreur de connexion HTTP: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur HTTP: {e}")
        return False
    
    return True

def test_webdav_endpoint():
    """Test spécifique de l'endpoint WebDAV"""
    print("\n🔧 Test de l'endpoint WebDAV...")
    print("=" * 50)
    
    webdav_url = os.getenv('NEXTCLOUD_WEBDAV_URL')
    user = os.getenv('NEXTCLOUD_USER')
    password = os.getenv('NEXTCLOUD_PASSWORD')
    
    print(f"🎯 URL testée: {webdav_url}")
    print(f"👤 Utilisateur: {user}")
    
    # Test avec timeout plus long
    try:
        response = requests.request(
            'PROPFIND',
            webdav_url,
            auth=(user, password),
            headers={'Depth': '0'},
            verify=False,
            timeout=30  # Timeout plus long
        )
        print(f"✅ Réponse WebDAV: {response.status_code}")
        
        if response.status_code == 207:
            print("✅ WebDAV fonctionne correctement")
            return True
        elif response.status_code == 401:
            print("❌ Erreur d'authentification")
            print("   Vérifiez vos identifiants dans le fichier .env")
            return False
        elif response.status_code == 404:
            print("❌ Endpoint WebDAV non trouvé")
            print("   Vérifiez l'URL WebDAV dans le fichier .env")
            return False
        else:
            print(f"⚠️  Réponse inattendue: {response.status_code}")
            print(f"   Contenu: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout lors de la requête WebDAV")
        print("   Le serveur met trop de temps à répondre")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Erreur de connexion WebDAV: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur WebDAV: {e}")
        return False

def test_alternative_urls():
    """Test d'URLs alternatives"""
    print("\n🔄 Test d'URLs alternatives...")
    print("=" * 50)
    
    user = os.getenv('NEXTCLOUD_USER')
    password = os.getenv('NEXTCLOUD_PASSWORD')
    
    # URLs alternatives à tester
    alternative_urls = [
        'https://capdrive.caplogy.com/remote.php/dav/files/t.frescaline/',
        'https://capdrive.caplogy.com/remote.php/webdav/',
        'https://capdrive.caplogy.com/remote.php/dav/files/admin/',
    ]
    
    for url in alternative_urls:
        print(f"\n🧪 Test de: {url}")
        try:
            response = requests.request(
                'PROPFIND',
                url,
                auth=(user, password),
                headers={'Depth': '0'},
                verify=False,
                timeout=10
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 207:
                print(f"   ✅ Cette URL fonctionne!")
                return url
            elif response.status_code == 401:
                print(f"   ❌ Authentification échouée")
            elif response.status_code == 404:
                print(f"   ❌ URL non trouvée")
            else:
                print(f"   ⚠️  Réponse: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 Diagnostic Capdrive")
    print("=" * 50)
    
    # Test de base
    if test_network_connectivity():
        print("\n" + "=" * 50)
        
        # Test WebDAV
        if not test_webdav_endpoint():
            print("\n" + "=" * 50)
            # Test d'alternatives
            working_url = test_alternative_urls()
            if working_url:
                print(f"\n💡 Suggestion: Utilisez cette URL dans votre .env:")
                print(f"   NEXTCLOUD_WEBDAV_URL={working_url}")
    
    print("\n👋 Fin du diagnostic")
