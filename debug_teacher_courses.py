#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier les cours des enseignants FaceTrack
"""

import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceTrack.settings')
django.setup()

from school.models import Enseignant, Cours, User
from django.utils import timezone

def debug_teacher_courses():
    """Diagnostique les cours des enseignants"""
    print("🔍 Diagnostic des cours des enseignants FaceTrack")
    print("=" * 60)
    
    try:
        # Vérifier tous les enseignants
        enseignants = Enseignant.objects.all()
        print(f"📚 {enseignants.count()} enseignant(s) trouvé(s)")
        print()
        
        today = timezone.now().date()
        print(f"📅 Date d'aujourd'hui: {today}")
        print()
        
        for enseignant in enseignants:
            print(f"👨‍🏫 Enseignant: {enseignant.user.get_full_name()}")
            print(f"   Username: {enseignant.user.username}")
            print(f"   Email: {enseignant.user.email}")
            print(f"   Rôle: {enseignant.user.role}")
            
            # Vérifier les cours d'aujourd'hui
            cours_aujourd_hui = Cours.objects.filter(
                enseignant=enseignant,
                date=today
            )
            
            print(f"   📚 Cours aujourd'hui: {cours_aujourd_hui.count()}")
            
            if cours_aujourd_hui.exists():
                for cours in cours_aujourd_hui:
                    print(f"      ✅ {cours.matiere.nom} - {cours.classe.nom} ({cours.heure_debut}-{cours.heure_fin})")
            else:
                print(f"      ❌ Aucun cours programmé aujourd'hui")
            
            # Vérifier tous les cours de cet enseignant
            total_cours = Cours.objects.filter(enseignant=enseignant).count()
            print(f"   📊 Total cours assignés: {total_cours}")
            
            if total_cours > 0:
                # Afficher quelques cours récents
                cours_recents = Cours.objects.filter(enseignant=enseignant).order_by('-date')[:3]
                print(f"   📅 Cours récents:")
                for cours in cours_recents:
                    print(f"      • {cours.date}: {cours.matiere.nom} - {cours.classe.nom}")
            
            print()
        
        # Vérifier les cours sans enseignant
        cours_sans_enseignant = Cours.objects.filter(enseignant__isnull=True).count()
        print(f"⚠️  Cours sans enseignant assigné: {cours_sans_enseignant}")
        
        if cours_sans_enseignant > 0:
            print("   Ces cours doivent être assignés à des enseignants !")
        
        print()
        print("💡 Solutions possibles:")
        print("   1. Vérifier que l'enseignant a des cours assignés pour aujourd'hui")
        print("   2. Créer des cours et les assigner via /admin/courses/")
        print("   3. Vérifier que la date des cours correspond à aujourd'hui")
        
    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {e}")

if __name__ == "__main__":
    debug_teacher_courses()
