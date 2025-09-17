# 🚀 Scripts de Création d'Utilisateurs FaceTrack

Ce dossier contient des scripts pour créer des utilisateurs de test réalistes pour l'application FaceTrack.

## 📁 Fichiers inclus

- **`create_realistic_users.py`** - Script principal de création d'utilisateurs
- **`verify_users_creation.py`** - Script de vérification des utilisateurs créés
- **`README_CREATION_UTILISATEURS.md`** - Ce fichier d'instructions

## 🎯 Objectif

Créer automatiquement :
- **25 élèves par classe** (8 classes = 200 élèves)
- **1 parent par élève** (200 parents)
- **1 enseignant par matière** (selon les matières existantes)
- **Total : ~400+ utilisateurs**

## ⚠️ Prérequis

Avant d'exécuter les scripts, assurez-vous d'avoir :

1. **Classes créées** dans la base de données
2. **Matières créées** dans la base de données
3. **Package Faker installé** : `pip install Faker`

## 🔧 Installation de Faker

```bash
pip install Faker
```

## 🚀 Utilisation

### 1. Créer les utilisateurs

```bash
python create_realistic_users.py
```

**Ce que fait ce script :**
- ✅ Vérifie l'existence des classes et matières
- ✅ Crée des enseignants pour chaque matière
- ✅ Crée 25 élèves par classe avec des données réalistes
- ✅ Crée un parent pour chaque élève
- ✅ Génère des matricules uniques pour chaque élève
- ✅ Utilise des noms et prénoms français courants
- ✅ Crée des adresses et téléphones fictifs

### 2. Vérifier la création

```bash
python verify_users_creation.py
```

**Ce que fait ce script :**
- 🔍 Compte tous les utilisateurs par rôle
- 🔍 Vérifie la cohérence parent-élève
- 🔍 Affiche les statistiques par classe
- 🔍 Montre des exemples d'utilisateurs créés

## 📊 Résultats attendus

Après exécution, vous devriez avoir :

```
📚 Classes traitées: 8
👨‍🏫 Enseignants créés: [nombre de matières]
👥 Élèves créés: 200
👨‍👩‍👧‍👦 Parents créés: 200
👤 Total utilisateurs: 400+
```

## 🔑 Informations de connexion

### Élèves
- **Username** : `eleve_nom_prenom_numero`
- **Password** : `eleve123`
- **Exemple** : `eleve_martin_emma_001`

### Parents
- **Username** : `parent_nom_prenom_numero`
- **Password** : `parent123`
- **Exemple** : `parent_martin_marie_001`

### Enseignants
- **Username** : `enseignant_nom_prenom`
- **Password** : `enseignant123`
- **Exemple** : `enseignant_dubois_lucas`

## 🎨 Caractéristiques des données

### Noms et prénoms
- **Prénoms français** : Emma, Lucas, Léa, Hugo, etc.
- **Noms de famille** : Martin, Bernard, Dubois, etc.
- **Répartition équilibrée** entre filles et garçons

### Données réalistes
- **Dates de naissance** : 10-18 ans pour les élèves
- **Adresses** : Adresses françaises fictives
- **Téléphones** : Numéros de téléphone français
- **Emails** : Format `username@facetrack.fr`

### Matricules
- **Format** : `2025_6_001` (année_niveau_numéro)
- **Uniques** : Pas de doublons
- **Séquentiels** : Numérotation par classe

## 🛡️ Sécurité

### ⚠️ ATTENTION
- **Mots de passe par défaut** : Changez-les en production !
- **Données fictives** : Ne pas utiliser en environnement réel
- **Base de données** : Faites une sauvegarde avant exécution

### 🔒 Recommandations
1. **Sauvegarde** de la base avant exécution
2. **Environnement de test** uniquement
3. **Changement des mots de passe** après création
4. **Suppression** des comptes de test en production

## 🐛 Dépannage

### Erreur : "Aucune classe trouvée"
**Solution** : Créez d'abord les classes via l'admin Django

### Erreur : "Aucune matière trouvée"
**Solution** : Créez d'abord les matières via l'admin Django

### Erreur : "Module Faker non trouvé"
**Solution** : `pip install Faker`

### Erreur : "Permission denied"
**Solution** : Vérifiez les permissions de la base de données

## 📝 Personnalisation

### Modifier le nombre d'élèves par classe
```python
# Dans create_realistic_users.py, ligne ~200
for i in range(1, 26):  # Changez 26 pour modifier le nombre
```

### Ajouter de nouveaux noms
```python
# Ajoutez dans les listes PRENOMS_FILLES, PRENOMS_GARCONS, NOMS_FAMILLE
PRENOMS_FILLES = ['Emma', 'Léa', 'Chloé', 'Votre_Nom', ...]
```

### Modifier les mots de passe
```python
# Dans les fonctions create_user_with_role
password="votre_nouveau_mot_de_passe"
```

## 🎉 Support

Si vous rencontrez des problèmes :
1. Vérifiez les prérequis
2. Consultez les logs d'erreur
3. Vérifiez la structure de la base de données
4. Assurez-vous que Django est correctement configuré

---

**Bon développement avec FaceTrack ! 🚀**
