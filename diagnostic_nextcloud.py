#!/usr/bin/env python3
"""
Diagnostic de connexion Nextcloud pour résoudre les problèmes de timeout.
"""

import os
import requests
import time
from urllib.parse import urlparse

class NextcloudDiagnostic:
    def __init__(self):
        self.webdav_url = os.getenv('NEXTCLOUD_WEBDAV_URL')
        self.share_url = os.getenv('NEXTCLOUD_SHARE_URL') 
        self.user = os.getenv('NEXTCLOUD_USER')
        self.password = os.getenv('NEXTCLOUD_PASSWORD')
        
        print("🔍 DIAGNOSTIC NEXTCLOUD")
        print("=" * 50)
        
    def check_environment(self):
        """Vérifier les variables d'environnement."""
        print("📋 1. Variables d'environnement:")
        
        vars_to_check = {
            'NEXTCLOUD_WEBDAV_URL': self.webdav_url,
            'NEXTCLOUD_SHARE_URL': self.share_url,
            'NEXTCLOUD_USER': self.user,
            'NEXTCLOUD_PASSWORD': '***' if self.password else None
        }
        
        missing = []
        for var, value in vars_to_check.items():
            if value:
                print(f"   ✅ {var}: {value}")
            else:
                print(f"   ❌ {var}: MANQUANT")
                missing.append(var)
        
        if missing:
            print(f"\n⚠️ Variables manquantes: {', '.join(missing)}")
            return False
        return True
    
    def test_basic_connectivity(self):
        """Test de connectivité de base."""
        print("\n🌐 2. Test de connectivité:")
        
        if not self.webdav_url:
            print("   ❌ Pas d'URL WebDAV configurée")
            return False
        
        # Extraire le domaine de base
        parsed = urlparse(self.webdav_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        try:
            print(f"   🔗 Test ping vers: {base_url}")
            response = requests.get(base_url, timeout=10)
            print(f"   ✅ Serveur accessible (Status: {response.status_code})")
            return True
        except requests.exceptions.Timeout:
            print("   ❌ Timeout - Serveur trop lent ou inaccessible")
            return False
        except requests.exceptions.ConnectionError:
            print("   ❌ Erreur de connexion - Serveur indisponible")
            return False
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    
    def test_webdav_auth(self):
        """Test d'authentification WebDAV."""
        print("\n🔐 3. Test authentification WebDAV:")
        
        if not all([self.webdav_url, self.user, self.password]):
            print("   ❌ Informations d'authentification incomplètes")
            return False
        
        try:
            print(f"   👤 Utilisateur: {self.user}")
            print(f"   🔗 URL: {self.webdav_url}")
            
            # Test PROPFIND simple avec timeout court
            response = requests.request(
                'PROPFIND',
                self.webdav_url,
                auth=(self.user, self.password),
                timeout=15,  # Timeout réduit
                headers={'Depth': '0'}
            )
            
            if response.status_code == 207:
                print("   ✅ Authentification WebDAV réussie")
                return True
            elif response.status_code == 401:
                print("   ❌ Erreur d'authentification - Vérifiez user/password")
                return False
            else:
                print(f"   ⚠️ Réponse inattendue: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print("   ❌ Timeout WebDAV - Connexion trop lente")
            return False
        except Exception as e:
            print(f"   ❌ Erreur WebDAV: {e}")
            return False
    
    def test_directory_listing(self):
        """Test de listage de répertoire avec timeout optimisé."""
        print("\n📁 4. Test listage répertoire:")
        
        if not all([self.webdav_url, self.user, self.password]):
            print("   ❌ Configuration incomplète")
            return False
        
        # Test sur le répertoire racine avec timeout réduit
        test_paths = [
            '/',
            '/Biblio_Cours_Caplogy/',
        ]
        
        for path in test_paths:
            try:
                url = self.webdav_url.rstrip('/') + path
                print(f"   📂 Test: {path}")
                
                start_time = time.time()
                response = requests.request(
                    'PROPFIND',
                    url,
                    auth=(self.user, self.password),
                    timeout=10,  # Timeout très court
                    headers={'Depth': '1'}
                )
                elapsed = time.time() - start_time
                
                if response.status_code == 207:
                    print(f"   ✅ Listage réussi en {elapsed:.2f}s")
                    
                    # Compter les éléments
                    content = response.text
                    folder_count = content.count('<d:collection/>')
                    file_count = content.count('<d:resourcetype/>') - folder_count
                    print(f"      📁 {folder_count} dossiers, 📄 {file_count} fichiers")
                    return True
                else:
                    print(f"   ❌ Erreur {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"   ❌ Timeout sur {path} (>10s)")
            except Exception as e:
                print(f"   ❌ Erreur sur {path}: {e}")
        
        return False
    
    def test_optimized_config(self):
        """Tester une configuration optimisée."""
        print("\n⚡ 5. Test configuration optimisée:")
        
        # Configuration avec timeouts réduits
        session = requests.Session()
        session.auth = (self.user, self.password)
        
        # Headers optimisés
        headers = {
            'User-Agent': 'Caplogy-Django/1.0',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }
        
        try:
            url = self.webdav_url
            print(f"   🚀 Test avec session optimisée")
            
            start_time = time.time()
            response = session.request(
                'PROPFIND',
                url,
                headers={**headers, 'Depth': '0'},
                timeout=8
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 207:
                print(f"   ✅ Connexion optimisée réussie en {elapsed:.2f}s")
                return True
            else:
                print(f"   ❌ Erreur {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print("   ❌ Timeout même avec configuration optimisée")
            return False
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    
    def generate_fixes(self):
        """Générer des solutions de correction."""
        print("\n🔧 SOLUTIONS RECOMMANDÉES:")
        print("=" * 50)
        
        print("1. 📊 Augmenter les timeouts dans nextcloud_api.py:")
        print("   - Changer timeout=30 vers timeout=60")
        print("   - Ajouter retry automatique")
        
        print("\n2. ⚡ Optimiser la connexion:")
        print("   - Utiliser une session réutilisable")
        print("   - Réduire la profondeur des PROPFIND")
        print("   - Activer la compression")
        
        print("\n3. 🔄 Configuration alternative:")
        print("   - Tester depuis un autre réseau")
        print("   - Vérifier les proxies/firewalls")
        print("   - Contacter l'administrateur Nextcloud")
        
        print("\n4. 🚀 Mise en cache:")
        print("   - Implémenter un cache Redis/Memcached")
        print("   - Sauvegarder les listings de répertoire")
        
    def run_full_diagnostic(self):
        """Lancer le diagnostic complet."""
        results = []
        
        results.append(self.check_environment())
        results.append(self.test_basic_connectivity())
        results.append(self.test_webdav_auth())
        results.append(self.test_directory_listing())
        results.append(self.test_optimized_config())
        
        print("\n" + "=" * 50)
        print("📊 RÉSULTATS DU DIAGNOSTIC")
        print("=" * 50)
        
        tests = [
            "Variables d'environnement",
            "Connectivité de base", 
            "Authentification WebDAV",
            "Listage répertoire",
            "Configuration optimisée"
        ]
        
        for i, (test, result) in enumerate(zip(tests, results)):
            status = "✅" if result else "❌"
            print(f"{status} {i+1}. {test}")
        
        success_count = sum(results)
        print(f"\n📈 Score: {success_count}/{len(results)} tests réussis")
        
        if success_count < 3:
            print("🚨 Problème de configuration détecté!")
            self.generate_fixes()
        elif success_count < 5:
            print("⚠️ Configuration partiellement fonctionnelle")
            self.generate_fixes()
        else:
            print("🎉 Configuration Nextcloud opérationnelle!")

def main():
    diagnostic = NextcloudDiagnostic()
    diagnostic.run_full_diagnostic()

if __name__ == "__main__":
    main()
