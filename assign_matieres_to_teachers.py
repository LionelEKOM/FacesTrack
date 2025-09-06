#!/usr/bin/env python
"""
Script pour assigner les matières aux enseignants existants
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceTrack.settings')
django.setup()

from django.contrib.auth import get_user_model
from school.models import User, Classe, Matiere, Eleve, Enseignant, Parent

User = get_user_model()

def assign_matieres_to_teachers():
    """Assigner les matières aux enseignants existants"""
    
    print("Assignation des matières aux enseignants...")
    
    # Récupérer tous les enseignants
    enseignants = Enseignant.objects.all()
    
    if not enseignants:
        print("⚠ Aucun enseignant trouvé.")
        return
    
    # Récupérer toutes les matières
    matieres = Matiere.objects.all()
    
    if not matieres:
        print("⚠ Aucune matière trouvée.")
        return
    
    # Assigner les matières selon le nom d'utilisateur
    for enseignant in enseignants:
        username = enseignant.user.username
        
        if 'math' in username:
            matiere = matieres.filter(nom__icontains='Mathématiques').first()
            if matiere:
                enseignant.matieres.add(matiere)
                enseignant.specialite = 'Mathématiques'
                print(f"✓ {enseignant.user.get_full_name()} -> Mathématiques")
        
        elif 'francais' in username:
            matiere = matieres.filter(nom__icontains='Français').first()
            if matiere:
                enseignant.matieres.add(matiere)
                enseignant.specialite = 'Français'
                print(f"✓ {enseignant.user.get_full_name()} -> Français")
        
        elif 'histoire' in username:
            matiere = matieres.filter(nom__icontains='Histoire').first()
            if matiere:
                enseignant.matieres.add(matiere)
                enseignant.specialite = 'Histoire-Géographie'
                print(f"✓ {enseignant.user.get_full_name()} -> Histoire-Géographie")
        
        else:
            # Assigner une matière par défaut
            matiere = matieres.first()
            if matiere:
                enseignant.matieres.add(matiere)
                enseignant.specialite = matiere.nom
                print(f"✓ {enseignant.user.get_full_name()} -> {matiere.nom} (par défaut)")
        
        enseignant.save()
    
    # Afficher le résumé
    print(f"\n=== RÉSUMÉ DES ASSIGNATIONS ===")
    for enseignant in enseignants:
        matieres_assigned = enseignant.matieres.all()
        print(f"{enseignant.user.get_full_name()}: {', '.join([m.nom for m in matieres_assigned])}")

if __name__ == '__main__':
    assign_matieres_to_teachers()
