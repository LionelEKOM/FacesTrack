#!/usr/bin/env python
"""
Script pour créer des utilisateurs de test dans la base de données FaceTrack
"""
import os
import sys
import django
from datetime import date, datetime
from django.utils import timezone

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceTrack.settings')
django.setup()

from django.contrib.auth import get_user_model
from school.models import User, Classe, Matiere, Eleve, Enseignant, Parent

User = get_user_model()

def create_test_users():
    """Créer des utilisateurs de test avec différents rôles"""
    
    print("Création des utilisateurs de test...")
    
    # 1. Créer un administrateur
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@facetrack.com',
            'first_name': 'Admin',
            'last_name': 'Système',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
            'date_naissance': date(1980, 1, 1),
            'adresse': '123 Rue Admin, Ville',
            'telephone': '+237 123456789'
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✓ Administrateur créé: {admin_user}")
    else:
        print(f"⚠ Administrateur existe déjà: {admin_user}")
    
    # 2. Créer des enseignants
    enseignants_data = [
        {
            'username': 'prof_math',
            'email': 'math@facetrack.com',
            'first_name': 'Marie',
            'last_name': 'Dubois',
            'role': 'ENSEIGNANT',
            'date_naissance': date(1985, 3, 15),
            'adresse': '456 Rue des Profs, Ville',
            'telephone': '+237 234567890'
        },
        {
            'username': 'prof_francais',
            'email': 'francais@facetrack.com',
            'first_name': 'Jean',
            'last_name': 'Martin',
            'role': 'ENSEIGNANT',
            'date_naissance': date(1982, 7, 22),
            'adresse': '789 Avenue des Enseignants, Ville',
            'telephone': '+237 345678901'
        },
        {
            'username': 'prof_histoire',
            'email': 'histoire@facetrack.com',
            'first_name': 'Sophie',
            'last_name': 'Bernard',
            'role': 'ENSEIGNANT',
            'date_naissance': date(1988, 11, 8),
            'adresse': '321 Boulevard de l\'Histoire, Ville',
            'telephone': '+237 456789012'
        }
    ]
    
    for enseignant_data in enseignants_data:
        user, created = User.objects.get_or_create(
            username=enseignant_data['username'],
            defaults=enseignant_data
        )
        if created:
            user.set_password('prof123')
            user.save()
            print(f"✓ Enseignant créé: {user}")
        else:
            print(f"⚠ Enseignant existe déjà: {user}")
    
    # 3. Créer des parents
    parents_data = [
        {
            'username': 'parent_dupont',
            'email': 'dupont@email.com',
            'first_name': 'Pierre',
            'last_name': 'Dupont',
            'role': 'PARENT',
            'date_naissance': date(1975, 5, 10),
            'adresse': '654 Rue des Parents, Ville',
            'telephone': '+237 567890123'
        },
        {
            'username': 'parent_durand',
            'email': 'durand@email.com',
            'first_name': 'Claire',
            'last_name': 'Durand',
            'role': 'PARENT',
            'date_naissance': date(1978, 9, 25),
            'adresse': '987 Avenue des Familles, Ville',
            'telephone': '+237 678901234'
        }
    ]
    
    for parent_data in parents_data:
        user, created = User.objects.get_or_create(
            username=parent_data['username'],
            defaults=parent_data
        )
        if created:
            user.set_password('parent123')
            user.save()
            print(f"✓ Parent créé: {user}")
        else:
            print(f"⚠ Parent existe déjà: {user}")
    
    # 4. Créer des élèves
    eleves_data = [
        {
            'username': 'eleve_dupont',
            'email': 'thomas.dupont@eleve.com',
            'first_name': 'Thomas',
            'last_name': 'Dupont',
            'role': 'ELEVE',
            'date_naissance': date(2008, 2, 14),
            'adresse': '654 Rue des Parents, Ville',
            'telephone': '+237 789012345'
        },
        {
            'username': 'eleve_durand',
            'email': 'lisa.durand@eleve.com',
            'first_name': 'Lisa',
            'last_name': 'Durand',
            'role': 'ELEVE',
            'date_naissance': date(2007, 8, 3),
            'adresse': '987 Avenue des Familles, Ville',
            'telephone': '+237 890123456'
        },
        {
            'username': 'eleve_martin',
            'email': 'paul.martin@eleve.com',
            'first_name': 'Paul',
            'last_name': 'Martin',
            'role': 'ELEVE',
            'date_naissance': date(2009, 12, 7),
            'adresse': '147 Rue des Étudiants, Ville',
            'telephone': '+237 901234567'
        },
        {
            'username': 'eleve_bernard',
            'email': 'emma.bernard@eleve.com',
            'first_name': 'Emma',
            'last_name': 'Bernard',
            'role': 'ELEVE',
            'date_naissance': date(2006, 4, 18),
            'adresse': '258 Boulevard des Jeunes, Ville',
            'telephone': '+237 012345678'
        }
    ]
    
    for eleve_data in eleves_data:
        user, created = User.objects.get_or_create(
            username=eleve_data['username'],
            defaults=eleve_data
        )
        if created:
            user.set_password('eleve123')
            user.save()
            print(f"✓ Élève créé: {user}")
        else:
            print(f"⚠ Élève existe déjà: {user}")
    
    print("\n=== RÉSUMÉ DES UTILISATEURS CRÉÉS ===")
    print("Administrateur:")
    print("  - Username: admin, Password: admin123")
    print("\nEnseignants:")
    print("  - Username: prof_math, Password: prof123")
    print("  - Username: prof_francais, Password: prof123")
    print("  - Username: prof_histoire, Password: prof123")
    print("\nParents:")
    print("  - Username: parent_dupont, Password: parent123")
    print("  - Username: parent_durand, Password: parent123")
    print("\nÉlèves:")
    print("  - Username: eleve_dupont, Password: eleve123")
    print("  - Username: eleve_durand, Password: eleve123")
    print("  - Username: eleve_martin, Password: eleve123")
    print("  - Username: eleve_bernard, Password: eleve123")

if __name__ == '__main__':
    create_test_users()
