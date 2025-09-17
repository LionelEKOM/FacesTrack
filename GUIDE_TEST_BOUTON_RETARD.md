# 🎯 Guide de Test - Bouton "Marquer en Retard"

## 📋 Fonctionnalité implémentée

Le bouton "Marquer en Retard" de la modal est maintenant **entièrement fonctionnel** et permet de marquer manuellement un élève en retard depuis l'interface de scan QR.

## ✅ Modifications apportées

1. **Bouton "Marquer comme Présent" supprimé** : Plus de confusion entre les actions manuelles et automatiques
2. **Bouton "Marquer en Retard" fonctionnel** : Permet de marquer un élève en retard manuellement
3. **Nouvelle API créée** : `/api/update-presence-from-scan/` pour gérer les mises à jour depuis l'interface de scan
4. **Gestion automatique** : La modal se ferme automatiquement après la mise à jour

## 🔧 Comment ça fonctionne

### ⚡ Processus de mise en retard
1. **Clic sur le bouton** : L'utilisateur clique sur "Marquer en Retard"
2. **Appel API** : La fonction `markEleveRetard()` est déclenchée
3. **Mise à jour** : L'API met à jour le statut de l'élève à "RETARD"
4. **Fermeture automatique** : La modal se ferme automatiquement
5. **Notification** : Un message confirme la mise à jour
6. **Interface mise à jour** : Le statut et les statistiques sont mis à jour en temps réel

### 📱 API utilisée
- **Endpoint** : `/api/update-presence-from-scan/`
- **Méthode** : POST
- **Paramètres** : `eleve_id`, `session_id`, `statut`
- **Sécurité** : Vérification que l'utilisateur est bien l'enseignant du cours

## 🧪 Comment tester

### Étape 1 : Démarrer le serveur
```bash
python manage.py runserver
```

### Étape 2 : Se connecter en tant qu'enseignant
- URL : `http://localhost:8000/login/`
- Utilisateur : `prof_francais`
- Mot de passe : `password123`

### Étape 3 : Démarrer un appel
1. Aller sur le dashboard enseignant
2. Cliquer sur "Démarrer l'appel" pour un cours
3. Vous serez redirigé vers l'interface de scan QR

### Étape 4 : Ouvrir la modal d'un élève
1. Cliquer sur un élève dans la liste
2. La modal s'ouvre avec le QR code et les informations
3. **Vérifier que le bouton "Marquer en Retard" est visible**

### Étape 5 : Tester le bouton "Marquer en Retard"
1. Cliquer sur le bouton "Marquer en Retard"
2. **L'élève doit être marqué en retard**
3. **La modal doit se fermer automatiquement**
4. **Une notification doit confirmer la mise à jour**
5. **Le statut de l'élève doit passer à "Retard" dans la liste**

### Étape 6 : Vérifier les statistiques
1. Regarder les cartes de statistiques en haut de la page
2. **Le compteur "Retards" doit avoir augmenté de 1**
3. **Le compteur "Absents" doit avoir diminué de 1**

## 🎉 Résultats attendus

### ✅ Bouton visible
- Le bouton "Marquer en Retard" est visible dans la modal
- Le bouton "Marquer comme Présent" n'est plus visible

### ✅ Fonctionnalité
- Clic sur le bouton déclenche la mise à jour
- L'élève est marqué en retard
- L'heure d'arrivée est enregistrée

### ✅ Interface
- Modal se ferme automatiquement
- Notification de confirmation affichée
- Statut de l'élève mis à jour en temps réel
- Statistiques mises à jour

### ✅ Données
- Statut enregistré en base de données
- Heure d'arrivée enregistrée
- Méthode de détection : "MANUEL"

## 🐛 Dépannage

### Problème : Bouton ne fonctionne pas
**Solutions possibles :**
1. Vérifier que l'API `/api/update-presence-from-scan/` est accessible
2. Vérifier la console du navigateur pour les erreurs JavaScript
3. Vérifier que l'utilisateur est bien connecté en tant qu'enseignant

### Problème : Modal ne se ferme pas
**Solution :** Vérifier que la fonction `closeEleveModal()` est bien appelée

### Problème : Statut ne se met pas à jour
**Solution :** Vérifier que la fonction `updateEleveStatus()` reçoit les bons paramètres

## 📊 Fonctionnalités disponibles

### ✅ Actions manuelles
- **Marquer en Retard** : Bouton fonctionnel pour marquer un élève en retard
- **Scanner QR Code (Simulation)** : Simulation du scan QR pour tests

### ✅ Actions automatiques
- **Fermeture automatique** : Modal se ferme après mise à jour
- **Mise à jour temps réel** : Interface mise à jour automatiquement
- **Notifications** : Messages de confirmation affichés

## 🎯 Avantages

1. **Simplicité** : Plus de bouton "Marquer comme Présent" pour éviter la confusion
2. **Fonctionnalité** : Bouton "Marquer en Retard" entièrement opérationnel
3. **UX améliorée** : Modal se ferme automatiquement après action
4. **Feedback immédiat** : Notifications et mises à jour en temps réel
5. **Sécurité** : Vérification des permissions enseignant
