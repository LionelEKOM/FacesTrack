#!/usr/bin/env python3
"""
Script de vérification des utilisateurs créés
Vérifie que tous les utilisateurs ont été créés correctement
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceTrack.settings')
django.setup()

from school.models import User, Classe, Eleve, Parent, Enseignant, Matiere
from django.db.models import Count

def verify_users():
    """Vérifie la création des utilisateurs"""
    print("🔍 VÉRIFICATION DES UTILISATEURS CRÉÉS")
    print("=" * 60)
    
    # Vérifier les classes
    classes = Classe.objects.all()
    print(f"📚 Classes trouvées: {classes.count()}")
    for classe in classes:
        print(f"  • {classe.nom}")
    
    # Vérifier les matières
    matieres = Matiere.objects.all()
    print(f"\n📖 Matières trouvées: {matieres.count()}")
    for matiere in matieres:
        print(f"  • {matiere.nom} ({matiere.code})")
    
    # Vérifier les utilisateurs par rôle
    print(f"\n👤 Utilisateurs par rôle:")
    for role in ['ELEVE', 'PARENT', 'ENSEIGNANT', 'ADMIN']:
        count = User.objects.filter(role=role).count()
        print(f"  • {role}: {count}")
    
    # Vérifier les élèves par classe
    print(f"\n👥 Élèves par classe:")
    for classe in classes:
        eleves_count = Eleve.objects.filter(classe=classe).count()
        print(f"  • {classe.nom}: {eleves_count} élèves")
    
    # Vérifier les enseignants par matière
    print(f"\n👨‍🏫 Enseignants par matière:")
    for matiere in matieres:
        enseignants_count = Enseignant.objects.filter(specialite=matiere).count()
        print(f"  • {matiere.nom}: {enseignants_count} enseignants")
    
    # Vérifier les relations parent-élève
    print(f"\n👨‍👩‍👧‍👦 Relations parent-élève:")
    eleves_sans_parent = Eleve.objects.filter(parent__isnull=True).count()
    parents_sans_eleve = Parent.objects.filter(eleve__isnull=True).count()
    print(f"  • Élèves sans parent: {eleves_sans_parent}")
    print(f"  • Parents sans élève: {parents_sans_eleve}")
    
    # Statistiques détaillées
    print(f"\n📊 STATISTIQUES DÉTAILLÉES")
    print("=" * 60)
    
    total_users = User.objects.count()
    total_eleves = Eleve.objects.count()
    total_parents = Parent.objects.count()
    total_enseignants = Enseignant.objects.count()
    
    print(f"Total utilisateurs: {total_users}")
    print(f"Total élèves: {total_eleves}")
    print(f"Total parents: {total_parents}")
    print(f"Total enseignants: {total_enseignants}")
    
    # Vérifier la cohérence
    if total_eleves == total_parents:
        print("✅ Cohérence parent-élève: OK")
    else:
        print("❌ Cohérence parent-élève: PROBLÈME")
    
    # Vérifier les classes vides
    classes_vides = []
    for classe in classes:
        if Eleve.objects.filter(classe=classe).count() == 0:
            classes_vides.append(classe.nom)
    
    if classes_vides:
        print(f"⚠️  Classes sans élèves: {', '.join(classes_vides)}")
    else:
        print("✅ Toutes les classes ont des élèves")
    
    # Vérifier les matières sans enseignant
    matieres_sans_enseignant = []
    for matiere in matieres:
        if Enseignant.objects.filter(specialite=matiere).count() == 0:
            matieres_sans_enseignant.append(matiere.nom)
    
    if matieres_sans_enseignant:
        print(f"⚠️  Matières sans enseignant: {', '.join(matieres_sans_enseignant)}")
    else:
        print("✅ Toutes les matières ont des enseignants")
    
    print("\n" + "=" * 60)
    print("🎯 VÉRIFICATION TERMINÉE")

def show_sample_users():
    """Affiche quelques exemples d'utilisateurs créés"""
    print("\n📋 EXEMPLES D'UTILISATEURS CRÉÉS")
    print("=" * 60)
    
    # Afficher quelques élèves
    print("\n👥 Exemples d'élèves:")
    eleves = Eleve.objects.select_related('user', 'classe', 'parent__user')[:5]
    for eleve in eleves:
        print(f"  • {eleve.user.first_name} {eleve.user.last_name}")
        print(f"    Classe: {eleve.classe.nom}, Matricule: {eleve.matricule}")
        print(f"    Parent: {eleve.parent.user.first_name} {eleve.parent.user.last_name}")
        print(f"    Username: {eleve.user.username}")
        print()
    
    # Afficher quelques enseignants
    print("👨‍🏫 Exemples d'enseignants:")
    enseignants = Enseignant.objects.select_related('user', 'specialite')[:3]
    for enseignant in enseignants:
        print(f"  • {enseignant.user.first_name} {enseignant.user.last_name}")
        print(f"    Matière: {enseignant.specialite.nom}")
        print(f"    Username: {enseignant.user.username}")
        print()

def main():
    """Fonction principale"""
    try:
        verify_users()
        show_sample_users()
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
