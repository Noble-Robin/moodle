# 🛠️ GUIDE DE DÉPANNAGE NEXTCLOUD

## Problème identifié
Timeout Nextcloud : "Nextcloud met trop de temps à répondre (>30s)"

## Solutions immédiates

### 1. Lancer le diagnostic
```bash
cd /path/to/your/moodle/project
python diagnostic_nextcloud.py
```

### 2. Vérifier vos variables d'environnement
Assurez-vous que votre `.env` contient :
```bash
NEXTCLOUD_WEBDAV_URL=https://capdrive.caplogy.com/remote.php/dav/files/t.frescaline/
NEXTCLOUD_SHARE_URL=https://capdrive.caplogy.com/ocs/v2.php/apps/files_sharing/api/v1/shares
NEXTCLOUD_USER=t.frescaline
NEXTCLOUD_PASSWORD=votre_mot_de_passe
```

### 3. Tester la connectivité manuellement
```bash
# Test ping du serveur
curl -I https://capdrive.caplogy.com/

# Test authentification WebDAV
curl -X PROPFIND \
  -u "t.frescaline:votre_mot_de_passe" \
  -H "Depth: 0" \
  "https://capdrive.caplogy.com/remote.php/dav/files/t.frescaline/" \
  --max-time 15
```

## Optimisations appliquées

### ✅ 1. Timeouts optimisés
- Timeout de connexion : 10s
- Timeout de lecture : 30s
- Retry automatique : 3 tentatives

### ✅ 2. Session réutilisable
- Connexion persistante
- Headers optimisés
- Compression activée

### ✅ 3. Gestion d'erreurs améliorée
- Messages d'erreur spécifiques
- Suggestions de résolution
- Codes d'erreur HTTP appropriés

## Messages d'erreur et solutions

### 🔴 "Timeout Nextcloud"
**Cause :** Serveur lent ou surchargé
**Solution :** 
- Réessayer dans quelques minutes
- Contacter l'administrateur Nextcloud
- Vérifier la stabilité du réseau

### 🔴 "Erreur de connexion Nextcloud"
**Cause :** Serveur indisponible ou problème réseau
**Solution :**
- Vérifier la connexion internet
- Vérifier que le serveur Nextcloud est en ligne
- Tester depuis un autre réseau

### 🔴 "Erreur d'authentification"
**Cause :** Identifiants incorrects
**Solution :**
- Vérifier NEXTCLOUD_USER et NEXTCLOUD_PASSWORD
- Tester la connexion via l'interface web Nextcloud
- Vérifier que le compte n'est pas verrouillé

## Tests recommandés

### Test 1 : Diagnostic complet
```bash
python diagnostic_nextcloud.py
```

### Test 2 : Test des plugins
```bash
python test_django_images.py
```

### Test 3 : Test de l'interface web
1. Aller dans votre application Django
2. Créer un nouveau cours
3. Essayer d'ajouter une ressource Nextcloud
4. Vérifier les logs dans la console

## Monitoring et maintenance

### Logs à surveiller
```bash
# Logs Django (dans votre terminal de développement)
[NextcloudAPI] Réponse reçue en X.XXs (Status: 207)
[NextcloudAPI] Résultat: X dossiers, X fichiers

# Logs d'erreur à rechercher
[NextcloudAPI TIMEOUT] 
[NextcloudAPI ERROR]
```

### Performances attendues
- ✅ Connexion : < 10s
- ✅ Listage répertoire : < 30s
- ✅ Upload fichier : < 60s

## Contact support

Si le problème persiste après avoir suivi ce guide :

1. **Collectez les informations :**
   - Résultat du diagnostic
   - Logs d'erreur complets
   - Configuration réseau (proxy, firewall)

2. **Contactez l'administrateur Nextcloud :**
   - Vérification de la charge serveur
   - Optimisation de la configuration WebDAV
   - Augmentation des timeouts côté serveur

3. **Solutions temporaires :**
   - Utiliser des URLs directes au lieu de Nextcloud
   - Implémenter un cache local
   - Réduire la taille des répertoires
