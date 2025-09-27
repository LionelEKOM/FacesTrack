# 👥 Utilisateurs de Test FaceTrack

Ce document contient toutes les informations sur les utilisateurs de test créés pour votre application FaceTrack.

## 📊 Statistiques Générales

- **Total utilisateurs** : 11
- **Administrateurs** : 1
- **Enseignants** : 3
- **Parents** : 2
- **Élèves** : 5

## 🔐 Administrateurs

### Super Admin

- **Nom complet** : Super Admin
- **Username** : `superadmin`
- **Email** : `superadmin@facetrack.com`
- **Mot de passe** : `admin123`
- **Rôle** : Administrateur système

## 👨‍🏫 Enseignants

### Marie Dubois (Mathématiques)

- **Username** : `prof_math`
- **Email** : `math@facetrack.com`
- **Mot de passe** : `prof123`
- **Spécialité** : Mathématiques
- **Matières** : Mathématiques

### Jean Martin (Français)

- **Username** : `prof_francais`
- **Email** : `francais@facetrack.com`
- **Mot de passe** : `prof123`
- **Spécialité** : Français
- **Matières** : Français

### Sophie Bernard (Histoire-Géographie)

- **Username** : `prof_histoire`
- **Email** : `histoire@facetrack.com`
- **Mot de passe** : `prof123`
- **Spécialité** : Histoire-Géographie
- **Matières** : Histoire-Géographie

## 👨‍👩‍👧‍👦 Parents

### Pierre Dupont

- **Username** : `parent_dupont`
- **Email** : `dupont@email.com`
- **Mot de passe** : `parent123`
- **Profession** : Ingénieur
- **Lieu de travail** : Société d'ingénierie
- **Enfant** : Thomas Dupont

### Claire Durand

- **Username** : `parent_durand`
- **Email** : `durand@email.com`
- **Mot de passe** : `parent123`
- **Profession** : Médecin
- **Lieu de travail** : Centre hospitalier
- **Enfant** : Lisa Durand

## 👨‍🎓 Élèves

### Thomas Dupont

- **Username** : `eleve_dupont`
- **Email** : `thomas.dupont@eleve.com`
- **Mot de passe** : `eleve123`
- **Matricule** : `2025-2-B74E`
- **Classe** : 6ème B
- **Parent** : Pierre Dupont

### Lisa Durand

- **Username** : `eleve_durand`
- **Email** : `lisa.durand@eleve.com`
- **Mot de passe** : `eleve123`
- **Matricule** : `2025-3-C1CF`
- **Classe** : 5ème A
- **Parent** : Claire Durand

### Paul Martin

- **Username** : `eleve_martin`
- **Email** : `paul.martin@eleve.com`
- **Mot de passe** : `eleve123`
- **Matricule** : `2025-4-19C6`
- **Classe** : 4ème A


### [Élève sans nom]

- **Username** : [généré automatiquement]
- **Matricule** : `2025-1-423F`
- **Classe** : 6ème A

## 📚 Données Supplémentaires

### Classes Disponibles (8 classes)

- **6ème A** : 1 élève
- **6ème B** : 1 élève
- **5ème A** : 1 élève
- **4ème A** : 1 élève
- **3ème A** : 1 élève
- **2nde** : 0 élève
- **1ère** : 0 élève
- **Terminale** : 0 élève

### Matières Disponibles (10 matières)

- **Mathématiques** (coef: 4)
- **Français** (coef: 3)
- **Histoire-Géographie** (coef: 2)
- **Sciences Physiques** (coef: 3)
- **Sciences de la Vie et de la Terre** (coef: 2)
- **Anglais** (coef: 2)
- **Espagnol** (coef: 1)
- **Éducation Physique et Sportive** (coef: 1)
- **Arts Plastiques** (coef: 1)
- **Informatique** (coef: 2)

## 🚀 Comment Utiliser

### 1. Démarrer le serveur

```bash
python manage.py runserver
```

### 2. Accéder à l'application

- **Interface d'administration** : http://127.0.0.1:8000/admin/
- **Application principale** : http://127.0.0.1:8000/

### 3. Se connecter avec différents rôles

#### Administrateur

- Connectez-vous avec `superadmin` / `admin123`
- Accès complet au système
- Gestion des utilisateurs, classes, matières

#### Enseignant

- Connectez-vous avec `prof_math`, `prof_francais`, ou `prof_histoire` / `prof123`
- Créer des cours
- Faire l'appel des élèves
- Consulter les présences

#### Parent

- Connectez-vous avec `parent_dupont` ou `parent_durand` / `parent123`
- Consulter les présences de vos enfants
- Recevoir des notifications

#### Élève

- Connectez-vous avec `eleve_dupont`, `eleve_durand`, etc. / `eleve123`
- Voir votre emploi du temps
- Consulter vos présences

## 💡 Conseils d'Utilisation

1. **Testez tous les rôles** : Connectez-vous avec différents utilisateurs pour tester toutes les fonctionnalités
2. **Créez des cours** : Utilisez les enseignants pour créer des cours et tester l'appel
3. **Testez la reconnaissance faciale** : Utilisez les photos de référence des élèves
4. **Vérifiez les notifications** : Testez l'envoi de notifications aux parents

## 🔧 Scripts Utiles

- `create_test_users.py` : Créer les utilisateurs de test
- `create_test_data.py` : Créer les données supplémentaires (classes, matières, etc.)
- `show_test_users.py` : Afficher un résumé complet des utilisateurs
- `setup_test_environment.py` : Script principal pour tout configurer

## 🎯 Prochaines Étapes

1. Tester l'interface d'administration
2. Créer des cours avec les enseignants
3. Tester la reconnaissance faciale
4. Vérifier les notifications
5. Tester les différents tableaux de bord

---

**env act** : `source .venv/bin/activate`

**Note** : Tous les mots de passe sont simples pour faciliter les tests. En production, utilisez des mots de passe sécurisés.
