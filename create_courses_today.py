#!/usr/bin/env python3
"""
Script pour créer des cours pour aujourd'hui avec des dates réelles
"""

import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceTrack.settings')
django.setup()

from school.models import Cours, Matiere, Classe, Enseignant
from django.utils import timezone
from datetime import datetime, timedelta

def create_courses_for_today():
    """Crée des cours pour aujourd'hui avec des dates réelles"""
    print("🚀 Création de cours pour aujourd'hui FaceTrack")
    print("=" * 60)
    
    try:
        # Vérifier qu'il y a des enseignants, matières et classes
        enseignants = Enseignant.objects.all()
        matieres = Matiere.objects.all()
        classes = Classe.objects.all()
        
        if not enseignants.exists():
            print("❌ Aucun enseignant trouvé. Créez d'abord des enseignants.")
            return False
        
        if not matieres.exists():
            print("❌ Aucune matière trouvée. Créez d'abord des matières.")
            return False
        
        if not classes.exists():
            print("❌ Aucune classe trouvée. Créez d'abord des classes.")
            return False
        
        print(f"📚 {enseignants.count()} enseignant(s) trouvé(s)")
        print(f"📖 {matieres.count()} matière(s) trouvée(s)")
        print(f"🏫 {classes.count()} classe(s) trouvée(s)")
        print()
        
        # Supprimer les cours existants pour éviter les doublons
        Cours.objects.all().delete()
        print("🧹 Cours existants supprimés")
        print()
        
        # Créer des cours pour aujourd'hui
        today = timezone.now().date()
        print(f"📅 Création de cours pour aujourd'hui: {today}")
        print()
        
        # Horaires typiques d'une journée scolaire
        horaires = [
            ('08:00', '09:00'),
            ('09:00', '10:00'),
            ('10:15', '11:15'),
            ('11:15', '12:15'),
            ('14:00', '15:00'),
            ('15:00', '16:00'),
            ('16:15', '17:15'),
        ]
        
        cours_crees = []
        
        # Créer des cours pour chaque classe aujourd'hui
        for i, classe in enumerate(classes):
            # Sélectionner une matière au hasard
            matiere = matieres[i % matieres.count()]
            
            # Sélectionner un enseignant au hasard
            enseignant = enseignants[i % enseignants.count()]
            
            # Créer 3-4 cours par classe
            for j in range(3):
                if j < len(horaires):
                    heure_debut, heure_fin = horaires[j]
                    
                    # Créer le cours pour AUJOURD'HUI
                    cours = Cours.objects.create(
                        matiere=matiere,
                        classe=classe,
                        enseignant=enseignant,
                        date=today,  # AUJOURD'HUI !
                        heure_debut=heure_debut,
                        heure_fin=heure_fin,
                        salle=f"Salle {100 + classe.id * 10 + j}"
                    )
                    
                    cours_crees.append(cours)
                    print(f"   ✅ {matiere.nom} - {classe.nom} - {heure_debut}-{heure_fin} - {enseignant.user.get_full_name()}")
        
        print()
        print("=" * 60)
        print(f"🎉 {len(cours_crees)} cours créés pour AUJOURD'HUI !")
        print()
        
        # Statistiques
        cours_aujourd_hui = Cours.objects.filter(date=today).count()
        print("📊 Statistiques:")
        print(f"   📅 Cours aujourd'hui: {cours_aujourd_hui}")
        print(f"   👨‍🏫 Enseignants avec cours: {Cours.objects.values('enseignant').distinct().count()}")
        print(f"   🏫 Classes avec cours: {Cours.objects.values('classe').distinct().count()}")
        print()
        
        # Vérifier que chaque enseignant a des cours
        print("👨‍🏫 Vérification des enseignants:")
        for enseignant in enseignants:
            cours_count = Cours.objects.filter(enseignant=enseignant, date=today).count()
            if cours_count > 0:
                print(f"   ✅ {enseignant.user.get_full_name()}: {cours_count} cours aujourd'hui")
            else:
                print(f"   ⚠️  {enseignant.user.get_full_name()}: Aucun cours aujourd'hui")
        
        print()
        print("💡 Maintenant les enseignants peuvent utiliser le système de scan QR code !")
        print("   Accédez à /enseignant/appels/ pour voir les cours du jour")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des cours: {e}")
        return False

def main():
    """Fonction principale"""
    success = create_courses_for_today()
    
    if success:
        print("\n🎯 Prochaines étapes:")
        print("   1. Connectez-vous en tant qu'enseignant")
        print("   2. Allez dans 'Appels du jour'")
        print("   3. Vous devriez voir vos cours d'aujourd'hui")
        print("   4. Cliquez sur 'Démarrer l'appel' pour utiliser le scan QR")
        print("\n🚀 Le système FaceTrack est maintenant prêt !")
    else:
        print("\n❌ Échec de la création des cours. Vérifiez la configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()
