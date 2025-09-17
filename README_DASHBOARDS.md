# 🚀 FaceTrack - Dashboards par Rôle

## 📋 Vue d'ensemble

FaceTrack propose des interfaces différenciées selon le rôle de l'utilisateur :

- **Administrateur** : Gestion globale du collège
- **Enseignant** : Gestion des classes et prise de présence
- **Élève** : Consultation de son emploi du temps et présences
- **Parent** : Suivi de la scolarité de son enfant

## 🛠️ Installation et Configuration

### 1. Créer les utilisateurs de test

```bash
python manage.py create_test_users
```

### 2. Appliquer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Démarrer le serveur

```bash
python manage.py runserver
```

## 👥 Utilisateurs de Test


| Rôle               | Identifiants             | Dashboard                |
| ------------------ | ------------------------ | ------------------------ |
| **Administrateur** | `admin` / `admin123`     | `/admin/dashboard/`      |
| **Enseignant**     | `teacher` / `teacher123` | `/enseignant/dashboard/` |
| **Élève**          | `student` / `student123` | `/eleve/dashboard/`      |
| **Parent**         | `parent` / `parent123`   | `/parent/dashboard/`     |

## 🎯 Fonctionnalités par Dashboard

### 🔧 Dashboard Administrateur

- **Statistiques globales** : Élèves, enseignants, parents, présences
- **Graphiques** : Évolution des présences, absences par classe
- **Activités récentes** : Feedbacks parents, notifications
- **Actions** : Export Excel/PDF, gestion système

### 👨‍🏫 Dashboard Enseignant

- **Statistiques rapides** : Cours du jour, élèves absents, taux de présence
- **Emploi du temps** : Planning détaillé avec statuts
- **Actions** : Démarrer l'appel (reconnaissance faciale), export des registres
- **Graphiques** : Vue d'ensemble hebdomadaire

### 👨‍🎓 Dashboard Élève

- **Vue d'ensemble** : Taux de présence, cours du jour, retards
- **Emploi du temps** : Planning quotidien avec statuts de présence
- **Activités récentes** : Présences confirmées, notifications
- **Graphiques** : Évolution hebdomadaire des présences

### 👨‍👩‍👧‍👦 Dashboard Parent

- **Suivi enfant** : Absences, retards, taux de présence, cours suivis
- **Emploi du temps** : Planning hebdomadaire de l'enfant
- **Notifications** : Absences/retards signalés en temps réel
- **Échanges** : Historique des feedbacks avec l'école

## 🎨 Design et Technologies

### **Couleurs du Projet**

- **Vert principal** : `#f79320`
- **Jaune accent** : `#00bf63`

### **Technologies Utilisées**

- **Frontend** : HTML5, CSS3, JavaScript ES6+
- **Framework CSS** : Bootstrap 5.3.3
- **Icônes** : Font Awesome 6.4.0
- **Graphiques** : Chart.js
- **Police** : Google Fonts (Poppins)
- **Backend** : Django 4.x

### **Fonctionnalités Techniques**

- **Responsive Design** : Adaptation mobile/tablette/desktop
- **Animations CSS** : Transitions fluides, effets de survol
- **JavaScript Moderne** : ES6+, modules, gestion d'événements
- **Architecture Modulaire** : CSS et JS séparés, templates Django

## 🔐 Sécurité et Authentification

- **Décorateur `@login_required`** sur tous les dashboards
- **Vérification des rôles** dans les vues
- **Redirection automatique** selon le rôle après connexion
- **Gestion des sessions** Django

## 📱 Responsive Design

### **Breakpoints**

- **Desktop** : ≥1024px (sidebar fixe)
- **Tablet** : 768px - 1023px (sidebar rétractable)
- **Mobile** : <768px (sidebar masquée, navigation adaptée)

### **Adaptations**

- **Grilles flexibles** : CSS Grid avec `auto-fit`
- **Navigation mobile** : Menu hamburger, sidebar overlay
- **Cartes adaptatives** : Taille et disposition optimisées
- **Typographie responsive** : Tailles de police adaptées

## 🚀 Développement et Personnalisation

### **Structure des Fichiers**

```
school/
├── templates/
│   ├── dashboard_base.html      # Template de base
│   ├── dashboard_admin.html     # Dashboard admin
│   ├── dashboard_teacher.html   # Dashboard enseignant
│   ├── dashboard_eleve.html     # Dashboard élève
│   └── dashboard_parent.html    # Dashboard parent
├── static/
│   ├── css/
│   │   ├── style.css           # Styles login
│   │   └── dashboard.css       # Styles dashboards
│   ├── js/
│   │   ├── script.js           # Scripts login
│   │   └── dashboard.js        # Scripts dashboards
│   └── imgs/
│       └── FaceTrack-logo.svg  # Logo du projet
└── views.py                    # Logique des vues
```

### **Personnalisation**

- **Couleurs** : Variables CSS dans `:root`
- **Layout** : Classes Bootstrap + CSS personnalisé
- **Fonctionnalités** : JavaScript modulaire et extensible
- **Contenu** : Templates Django avec blocs personnalisables

## 🐛 Dépannage

### **Problèmes Courants**

1. **Dashboard ne s'affiche pas**

   - Vérifier que l'utilisateur est connecté
   - Vérifier que le rôle est correctement défini
   - Consulter les logs Django

2. **Styles non chargés**

   - Vérifier que `python manage.py collectstatic` a été exécuté
   - Vérifier les chemins des fichiers statiques
   - Consulter la console du navigateur

3. **Graphiques non affichés**
   - Vérifier que Chart.js est chargé
   - Consulter la console JavaScript
   - Vérifier les IDs des canvas

### **Logs et Debug**

```bash
# Activer le mode debug
python manage.py runserver --verbosity 2

# Vérifier les migrations
python manage.py showmigrations

# Créer un superuser
python manage.py createsuperuser
```

## 📞 Support et Contact

Pour toute question ou problème :

- **Documentation** : Consulter ce README
- **Issues** : Créer une issue sur le repository
- **Développement** : Contacter l'équipe FaceTrack
- **Contactez** : https://wa.me/+237659160779


---

**FaceTrack** - Système de reconnaissance faciale pour la gestion des présences scolaires 🎓✨
