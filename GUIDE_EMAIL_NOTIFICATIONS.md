# 📧 Guide des Notifications Email aux Parents

## 🎯 Vue d'ensemble

Le système FaceTrack envoie automatiquement des emails aux parents pour les informer du statut de présence de leurs enfants. Trois types de notifications sont envoyés :

- ✅ **Confirmation de présence** : Quand l'enfant est présent en cours
- ⏰ **Notification de retard** : Quand l'enfant arrive en retard
- ⚠️ **Notification d'absence** : Quand l'enfant est absent

## 🚀 Fonctionnement

### Déclenchement automatique

Les emails sont envoyés automatiquement dans les cas suivants :

1. **Scan QR Code depuis smartphone** : Quand un parent scanne le QR code de son enfant
2. **Validation manuelle par l'enseignant** : Quand l'enseignant marque manuellement la présence
3. **Mise à jour via l'interface de scan** : Quand l'enseignant utilise l'interface de scan QR

### Conditions d'envoi

- L'élève doit avoir un parent associé dans la base de données
- Le parent doit avoir une adresse email valide
- Le système d'email doit être correctement configuré

## ⚙️ Configuration

### 1. Configuration Email (settings.py)

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Ou votre serveur SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # À configurer
EMAIL_HOST_PASSWORD = 'your-app-password'  # À configurer
DEFAULT_FROM_EMAIL = 'FaceTrack <your-email@gmail.com>'

# Configuration pour développement (console)
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### 2. Configuration Gmail (Recommandé)

1. **Activer l'authentification à deux facteurs** sur votre compte Gmail
2. **Générer un mot de passe d'application** :
   - Aller dans les paramètres Google
   - Sécurité → Authentification à deux facteurs
   - Mots de passe d'application → Générer
3. **Utiliser ce mot de passe** dans `EMAIL_HOST_PASSWORD`

### 3. Configuration Production

Pour la production, utilisez un service SMTP professionnel comme :
- **SendGrid**
- **Mailgun**
- **Amazon SES**
- **Postmark**

## 📧 Templates d'Email

### Structure des templates

Les templates sont situés dans `school/templates/emails/` :

- `presence_confirmation.html` : Confirmation de présence
- `absence_notification.html` : Notification d'absence
- `retard_notification.html` : Notification de retard

### Personnalisation

Chaque template contient :
- **En-tête** : Logo et titre de l'école
- **Informations de l'élève** : Nom, classe, heure d'arrivée
- **Détails du cours** : Matière, date, horaire, salle, enseignant
- **Message contextuel** : Selon le type de notification
- **Pied de page** : Coordonnées de l'école

## 🧪 Tests

### Test manuel

```bash
python test_email_notifications.py
```

Ce script teste :
- La création d'une présence de test
- L'envoi des trois types d'emails
- La validation des données

### Test en développement

En mode DEBUG, les emails sont affichés dans la console Django :
```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: ✅ Présence confirmée - [Nom Élève] - [Matière]
From: FaceTrack <your-email@gmail.com>
To: parent@example.com
Date: [Date]

[Contenu de l'email]
```

## 🔧 Intégration dans le Code

### Service d'Email

Le service `ParentNotificationService` dans `school/email_service.py` :

```python
# Envoi de confirmation de présence
ParentNotificationService.send_presence_confirmation_email(presence_id)

# Envoi de notification de retard
ParentNotificationService.send_retard_notification_email(presence_id)

# Envoi de notification d'absence
ParentNotificationService.send_absence_notification_email(presence_id)
```

### Intégration dans les Vues

Les emails sont automatiquement envoyés dans :

1. **api_mobile_checkin** : Quand la présence est confirmée depuis le smartphone
2. **api_update_presence_from_scan** : Quand l'enseignant met à jour le statut

## 📊 Logs et Monitoring

### Logs d'activité

Le système enregistre les tentatives d'envoi dans les logs Django :

```python
logger.info(f"Email de confirmation envoyé avec succès à {parent.user.email}")
logger.error(f"Échec de l'envoi de l'email à {parent.user.email}")
```

### Vérification des envois

Pour vérifier si un email a été envoyé :

1. **En développement** : Vérifier la console Django
2. **En production** : Vérifier les logs du serveur
3. **Via l'interface** : Les notifications sont aussi créées en base de données

## 🛠️ Dépannage

### Problèmes courants

1. **Email non reçu** :
   - Vérifier la configuration SMTP
   - Vérifier que l'email du parent est valide
   - Vérifier les logs d'erreur

2. **Erreur SMTP** :
   - Vérifier les identifiants Gmail
   - Vérifier que l'authentification à deux facteurs est activée
   - Vérifier le mot de passe d'application

3. **Template non trouvé** :
   - Vérifier que les templates sont dans le bon dossier
   - Vérifier les permissions de fichiers

### Debug

Pour activer le debug des emails :

```python
# Dans settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'school.email_service': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 📈 Statistiques

### Métriques à surveiller

- **Taux de livraison** : Pourcentage d'emails livrés
- **Taux d'ouverture** : Pourcentage d'emails ouverts par les parents
- **Taux de clic** : Pourcentage de clics sur les liens dans les emails
- **Temps de livraison** : Délai entre l'envoi et la réception

### Améliorations possibles

1. **Notifications push** : Ajouter des notifications push en plus des emails
2. **SMS** : Envoyer des SMS pour les notifications urgentes
3. **Personnalisation** : Permettre aux parents de choisir leurs préférences
4. **Rapports** : Générer des rapports de présence hebdomadaires/mensuels

## 🔒 Sécurité

### Bonnes pratiques

1. **Chiffrement** : Utiliser TLS pour les emails
2. **Authentification** : Utiliser des mots de passe d'application
3. **Validation** : Valider les adresses email des parents
4. **Rate limiting** : Limiter le nombre d'emails par parent
5. **Logs** : Enregistrer toutes les tentatives d'envoi

### Conformité RGPD

1. **Consentement** : Obtenir le consentement des parents
2. **Droit de retrait** : Permettre aux parents de se désabonner
3. **Données personnelles** : Minimiser les données personnelles dans les emails
4. **Rétention** : Définir une politique de rétention des emails

## 📞 Support

Pour toute question ou problème :

1. **Vérifier les logs** Django
2. **Tester avec le script** `test_email_notifications.py`
3. **Vérifier la configuration** SMTP
4. **Consulter la documentation** Django sur l'envoi d'emails

---

*Dernière mise à jour : [Date]*
*Version : 1.0*
