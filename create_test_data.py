#!/usr/bin/env python
"""
Script pour créer des données de test supplémentaires dans la base de données FaceTrack
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

def create_test_data():
    """Créer des données de test supplémentaires"""
    
    print("Création des données de test supplémentaires...")
    
    # 1. Créer des classes
    classes_data = [
        {'nom': '6A', 'cycle': 'PREMIER', 'annee_scolaire': '2024-2025', 'capacite': 30},
        {'nom': '6B', 'cycle': 'PREMIER', 'annee_scolaire': '2024-2025', 'capacite': 28},
        {'nom': '5A', 'cycle': 'PREMIER', 'annee_scolaire': '2024-2025', 'capacite': 32},
        {'nom': '4A', 'cycle': 'PREMIER', 'annee_scolaire': '2024-2025', 'capacite': 29},
        {'nom': '3A', 'cycle': 'PREMIER', 'annee_scolaire': '2024-2025', 'capacite': 31},
        {'nom': '2ND', 'cycle': 'SECOND', 'annee_scolaire': '2024-2025', 'capacite': 35},
        {'nom': '1ERE', 'cycle': 'SECOND', 'annee_scolaire': '2024-2025', 'capacite': 33},
        {'nom': 'TLE', 'cycle': 'SECOND', 'annee_scolaire': '2024-2025', 'capacite': 30},
    ]
    
    classes_created = []
    for classe_data in classes_data:
        classe, created = Classe.objects.get_or_create(
            nom=classe_data['nom'],
            annee_scolaire=classe_data['annee_scolaire'],
            defaults=classe_data
        )
        classes_created.append(classe)  # Ajouter toutes les classes, créées ou existantes
        if created:
            print(f"✓ Classe créée: {classe}")
        else:
            print(f"⚠ Classe existe déjà: {classe}")
    
    # 2. Créer des matières
    matieres_data = [
        {'nom': 'Mathématiques', 'description': 'Algèbre, géométrie et arithmétique', 'coefficient': 4},
        {'nom': 'Français', 'description': 'Grammaire, littérature et expression écrite', 'coefficient': 3},
        {'nom': 'Histoire-Géographie', 'description': 'Histoire mondiale et géographie', 'coefficient': 2},
        {'nom': 'Sciences Physiques', 'description': 'Physique et chimie', 'coefficient': 3},
        {'nom': 'Sciences de la Vie et de la Terre', 'description': 'Biologie et géologie', 'coefficient': 2},
        {'nom': 'Anglais', 'description': 'Langue anglaise et civilisation', 'coefficient': 2},
        {'nom': 'Espagnol', 'description': 'Langue espagnole et civilisation', 'coefficient': 1},
        {'nom': 'Éducation Physique et Sportive', 'description': 'Sports et activités physiques', 'coefficient': 1},
        {'nom': 'Arts Plastiques', 'description': 'Dessin, peinture et arts visuels', 'coefficient': 1},
        {'nom': 'Informatique', 'description': 'Programmation et technologies numériques', 'coefficient': 2},
    ]
    
    matieres_created = []
    for matiere_data in matieres_data:
        matiere, created = Matiere.objects.get_or_create(
            nom=matiere_data['nom'],
            defaults=matiere_data
        )
        matieres_created.append(matiere)  # Ajouter toutes les matières, créées ou existantes
        if created:
            print(f"✓ Matière créée: {matiere}")
        else:
            print(f"⚠ Matière existe déjà: {matiere}")
    
    # 3. Créer les profils d'enseignants
    enseignants_users = User.objects.filter(role='ENSEIGNANT')
    for user in enseignants_users:
        enseignant, created = Enseignant.objects.get_or_create(
            user=user,
            defaults={
                'date_embauche': date(2020, 9, 1),
                'specialite': 'Général'
            }
        )
        if created:
            # Assigner des matières selon le nom d'utilisateur
            if 'math' in user.username:
                matiere_math = next((m for m in matieres_created if 'Mathématiques' in m.nom), None)
                if matiere_math:
                    enseignant.matieres.add(matiere_math)
                enseignant.specialite = 'Mathématiques'
            elif 'francais' in user.username:
                matiere_francais = next((m for m in matieres_created if 'Français' in m.nom), None)
                if matiere_francais:
                    enseignant.matieres.add(matiere_francais)
                enseignant.specialite = 'Français'
            elif 'histoire' in user.username:
                matiere_histoire = next((m for m in matieres_created if 'Histoire' in m.nom), None)
                if matiere_histoire:
                    enseignant.matieres.add(matiere_histoire)
                enseignant.specialite = 'Histoire-Géographie'
            
            # Assigner quelques classes
            if classes_created:
                enseignant.classes.add(classes_created[0], classes_created[1])
            
            print(f"✓ Profil enseignant créé: {enseignant}")
        else:
            print(f"⚠ Profil enseignant existe déjà: {enseignant}")
    
    # 4. Créer les profils de parents
    parents_users = User.objects.filter(role='PARENT')
    for user in parents_users:
        parent, created = Parent.objects.get_or_create(
            user=user,
            defaults={
                'profession': 'Employé',
                'lieu_travail': 'Entreprise locale'
            }
        )
        if created:
            if 'dupont' in user.username:
                parent.profession = 'Ingénieur'
                parent.lieu_travail = 'Société d\'ingénierie'
            elif 'durand' in user.username:
                parent.profession = 'Médecin'
                parent.lieu_travail = 'Centre hospitalier'
            parent.save()
            print(f"✓ Profil parent créé: {parent}")
        else:
            print(f"⚠ Profil parent existe déjà: {parent}")
    
    # 5. Créer les profils d'élèves
    eleves_users = User.objects.filter(role='ELEVE')
    if classes_created:
        for i, user in enumerate(eleves_users):
            # Assigner une classe de manière cyclique
            classe = classes_created[i % len(classes_created)]
            
            # Trouver le parent correspondant
            parent = None
            if 'dupont' in user.username:
                parent = Parent.objects.filter(user__username='parent_dupont').first()
            elif 'durand' in user.username:
                parent = Parent.objects.filter(user__username='parent_durand').first()
            
            eleve, created = Eleve.objects.get_or_create(
                user=user,
                defaults={
                    'classe': classe,
                    'parent': parent
                }
            )
            if created:
                print(f"✓ Profil élève créé: {eleve}")
            else:
                print(f"⚠ Profil élève existe déjà: {eleve}")
    else:
        print("⚠ Aucune classe créée, impossible de créer les profils d'élèves")
    
    print("\n=== RÉSUMÉ DES DONNÉES CRÉÉES ===")
    print(f"Classes créées: {len(classes_created)}")
    print(f"Matières créées: {len(matieres_created)}")
    print(f"Profils enseignants créés: {Enseignant.objects.count()}")
    print(f"Profils parents créés: {Parent.objects.count()}")
    print(f"Profils élèves créés: {Eleve.objects.count()}")

if __name__ == '__main__':
    create_test_data()
