#!/usr/bin/env python3
"""
Script de création d'utilisateurs réalistes pour FaceTrack
Crée 25 élèves par classe et leurs parents correspondants
"""

import os
import sys
import django
from datetime import date, timedelta
import random
from faker import Faker

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceTrack.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from school.models import User, Classe, Eleve, Parent, Enseignant, Matiere
from django.db import transaction

# Initialiser Faker pour des données réalistes
fake = Faker(['fr_FR'])

# Noms et prénoms français courants
PRENOMS_FILLES = [
    'Emma', 'Léa', 'Chloé', 'Jade', 'Alice', 'Lola', 'Manon', 'Jasmine', 'Inès', 'Louise',
    'Camille', 'Sarah', 'Clara', 'Eva', 'Léna', 'Zoé', 'Nina', 'Maëlys', 'Léonie', 'Romane',
    'Agathe', 'Julia', 'Léana', 'Mya', 'Emy', 'Luna', 'Théa', 'Lola', 'Nora', 'Anaïs'
]

PRENOMS_GARCONS = [
    'Lucas', 'Hugo', 'Jules', 'Léo', 'Adam', 'Raphaël', 'Arthur', 'Louis', 'Ethan', 'Paul',
    'Antoine', 'Nathan', 'Tom', 'Théo', 'Eliott', 'Maxime', 'Enzo', 'Axel', 'Clément', 'Baptiste',
    'Alexandre', 'Victor', 'Gabriel', 'Timéo', 'Romain', 'Mathis', 'Evan', 'Noah', 'Sacha', 'Liam'
]

NOMS_FAMILLE = [
    'Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert', 'Richard', 'Petit', 'Durand', 'Leroy', 'Moreau',
    'Simon', 'Laurent', 'Lefebvre', 'Michel', 'Garcia', 'David', 'Bertrand', 'Roux', 'Vincent', 'Fournier',
    'Morel', 'Girard', 'Andre', 'Lefevre', 'Mercier', 'Dupont', 'Lambert', 'Bonnet', 'Francois', 'Martinez'
]

# Cette constante n'est plus utilisée car nous récupérons les classes depuis la base de données

def create_user_with_role(username, email, password, role, first_name, last_name):
    """Crée un utilisateur avec un rôle spécifique"""
    try:
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_active=True,
            date_joined=date.today(),
            telephone=fake.phone_number(),
            adresse=fake.address()
        )
        return user
    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur {username}: {e}")
        return None

# La fonction generate_matricule n'est plus nécessaire car le matricule est généré automatiquement par le modèle

def create_eleve_with_parent(classe, numero):
    """Crée un élève et son parent correspondant"""
    
    # Déterminer le genre de l'élève
    is_fille = random.choice([True, False])
    prenoms = PRENOMS_FILLES if is_fille else PRENOMS_GARCONS
    prenom_eleve = random.choice(prenoms)
    nom_famille = random.choice(NOMS_FAMILLE)
    
    # Créer le parent
    prenom_parent = random.choice(PRENOMS_FILLES + PRENOMS_GARCONS)
    username_parent = f"parent_{nom_famille.lower()}_{prenom_parent.lower()}_{numero}"
    email_parent = f"{username_parent}@facetrack.fr"
    
    parent_user = create_user_with_role(
        username=username_parent,
        email=email_parent,
        password="parent123",
        role="PARENT",
        first_name=prenom_parent,
        last_name=nom_famille
    )
    
    if not parent_user:
        return None, None
    
    # Créer l'objet Parent
    try:
        parent = Parent.objects.create(
            user=parent_user,
            profession=fake.job(),
            lieu_travail=fake.company()
        )
    except Exception as e:
        print(f"Erreur lors de la création du parent {username_parent}: {e}")
        parent_user.delete()
        return None, None
    
    # Créer l'élève
    username_eleve = f"eleve_{nom_famille.lower()}_{prenom_eleve.lower()}_{numero}"
    email_eleve = f"{username_eleve}@facetrack.fr"
    
    eleve_user = create_user_with_role(
        username=username_eleve,
        email=email_eleve,
        password="eleve123",
        role="ELEVE",
        first_name=prenom_eleve,
        last_name=nom_famille
    )
    
    # Mettre à jour la date de naissance dans l'utilisateur
    if eleve_user:
        eleve_user.date_naissance = fake.date_of_birth(minimum_age=10, maximum_age=18)
        eleve_user.save()
    
    if not eleve_user:
        parent_user.delete()
        parent.delete()
        return None, None
    
    # Créer l'objet Eleve (le matricule sera généré automatiquement)
    try:
        eleve = Eleve.objects.create(
            user=eleve_user,
            classe=classe,
            parent=parent
        )
    except Exception as e:
        print(f"Erreur lors de la création de l'élève {username_eleve}: {e}")
        eleve_user.delete()
        parent_user.delete()
        parent.delete()
        return None, None
    
    return eleve, parent

def create_enseignants():
    """Crée des enseignants pour les matières"""
    matieres = Matiere.objects.all()
    enseignants_crees = []
    
    for matiere in matieres:
        prenom = random.choice(PRENOMS_FILLES + PRENOMS_GARCONS)
        nom = random.choice(NOMS_FAMILLE)
        username = f"enseignant_{nom.lower()}_{prenom.lower()}"
        email = f"{username}@facetrack.fr"
        
        enseignant_user = create_user_with_role(
            username=username,
            email=email,
            password="enseignant123",
            role="ENSEIGNANT",
            first_name=prenom,
            last_name=nom
        )
        
        if enseignant_user:
            try:
                enseignant = Enseignant.objects.create(
                    user=enseignant_user,
                    specialite=matiere,
                    date_embauche=fake.date_between(start_date='-10y', end_date='-1y')
                )
                # Ajouter la matière à l'enseignant
                enseignant.matieres.add(matiere)
                # Ajouter quelques classes à l'enseignant
                classes_enseignant = Classe.objects.all()[:3]  # Prendre les 3 premières classes
                enseignant.classes.add(*classes_enseignant)
                
                enseignants_crees.append(enseignant)
                print(f"✅ Enseignant créé: {prenom} {nom} - {matiere.nom}")
            except Exception as e:
                print(f"❌ Erreur lors de la création de l'enseignant {username}: {e}")
                enseignant_user.delete()
    
    return enseignants_crees

def main():
    """Fonction principale"""
    print("🚀 Début de la création des utilisateurs réalistes...")
    print("=" * 60)
    
    # Vérifier que les classes existent
    classes = Classe.objects.all()
    if not classes.exists():
        print("❌ Aucune classe trouvée. Créez d'abord les classes.")
        return
    
    print(f"📚 Classes trouvées: {classes.count()}")
    
    # Vérifier que les matières existent
    matieres = Matiere.objects.all()
    if not matieres.exists():
        print("❌ Aucune matière trouvée. Créez d'abord les matières.")
        return
    
    print(f"📖 Matières trouvées: {matieres.count()}")
    
    # Créer des enseignants
    print("\n👨‍🏫 Création des enseignants...")
    enseignants = create_enseignants()
    
    # Créer des élèves et parents pour chaque classe
    total_eleves = 0
    total_parents = 0
    
    with transaction.atomic():
        for classe in classes:
            print(f"\n👥 Création des utilisateurs pour la classe {classe.nom}...")
            
            eleves_classe = 0
            parents_classe = 0
            
            for i in range(1, 26):  # 25 élèves par classe
                eleve, parent = create_eleve_with_parent(classe, i)
                
                if eleve and parent:
                    eleves_classe += 1
                    parents_classe += 1
                    print(f"  ✅ Élève {eleve.user.first_name} {eleve.user.last_name} créé (Parent: {parent.user.first_name} {parent.user.last_name})")
                else:
                    print(f"  ❌ Échec de création de l'élève {i} pour la classe {classe.nom}")
            
            total_eleves += eleves_classe
            total_parents += parents_classe
            
            print(f"  📊 Classe {classe.nom}: {eleves_classe} élèves et {parents_classe} parents créés")
    
    # Résumé final
    print("\n" + "=" * 60)
    print("🎉 CRÉATION TERMINÉE !")
    print("=" * 60)
    print(f"📚 Classes traitées: {classes.count()}")
    print(f"👨‍🏫 Enseignants créés: {len(enseignants)}")
    print(f"👥 Élèves créés: {total_eleves}")
    print(f"👨‍👩‍👧‍👦 Parents créés: {total_parents}")
    print(f"👤 Total utilisateurs: {total_eleves + total_parents + len(enseignants)}")
    
    print("\n🔑 Informations de connexion:")
    print("  • Élèves: username = eleve_nom_prenom_numero, password = eleve123")
    print("  • Parents: username = parent_nom_prenom_numero, password = parent123")
    print("  • Enseignants: username = enseignant_nom_prenom, password = enseignant123")
    
    print("\n⚠️  ATTENTION: Changez ces mots de passe en production !")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Création interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
