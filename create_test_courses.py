#!/usr/bin/env python3
"""
Script pour créer des cours de test et les assigner aux enseignants FaceTrack
Ce script permet de tester le système de scan QR code en créant des cours
"""

import os
import sys
import django
from django.conf import settings
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceTrack.settings')
django.setup()

from school.models import Cours, Matiere, Classe, Enseignant
from django.utils import timezone

def create_test_courses():
    """Crée des cours de test pour les enseignants"""
    print("🚀 Création de cours de test pour FaceTrack")
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
        
        # Créer des cours pour cette semaine
        today = timezone.now().date()
        cours_crees = []
        
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
        
        # Créer des cours pour les 5 prochains jours ouvrables
        for jour in range(5):
            date_cours = today + timedelta(days=jour)
            
            # Éviter les weekends
            if date_cours.weekday() >= 5:  # Samedi = 5, Dimanche = 6
            continue
        
            print(f"📅 Création des cours pour le {date_cours.strftime('%A %d/%m/%Y')}")
            
            # Assigner des cours à chaque classe
            for classe in classes:
                # Sélectionner une matière au hasard
                matiere = matieres[classe.id % matieres.count()]
                
                # Sélectionner un enseignant au hasard
                enseignant = enseignants[classe.id % enseignants.count()]
                
                # Créer 3-4 cours par classe par jour
                for i in range(3):
                    if i < len(horaires):
                        heure_debut, heure_fin = horaires[i]
            
            # Créer le cours
                        cours = Cours.objects.create(
                matiere=matiere,
                classe=classe,
                enseignant=enseignant,
                            date=date_cours,
                heure_debut=heure_debut,
                heure_fin=heure_fin,
                            salle=f"Salle {100 + classe.id * 10 + i}"
                        )
                        
                        cours_crees.append(cours)
                        print(f"   ✅ {matiere.nom} - {classe.nom} - {heure_debut}-{heure_fin} - {enseignant.user.get_full_name()}")
            
            print()
        
        # Créer des cours pour aujourd'hui spécifiquement (pour les tests)
        print("🎯 Création de cours pour aujourd'hui (tests)")
        for i, classe in enumerate(classes):
            matiere = matieres[i % matieres.count()]
            enseignant = enseignants[i % enseignants.count()]
            
            # Cours de test pour aujourd'hui
            cours_test = Cours.objects.create(
            matiere=matiere,
            classe=classe,
            enseignant=enseignant,
                date=today,
                heure_debut="10:00",
                heure_fin="11:00",
                salle=f"Salle Test {classe.nom}"
            )
            
            cours_crees.append(cours_test)
            print(f"   ✅ COURS TEST: {matiere.nom} - {classe.nom} - 10:00-11:00 - {enseignant.user.get_full_name()}")
        
        print()
        print("=" * 60)
        print(f"🎉 {len(cours_crees)} cours créés avec succès !")
        print()
        
        # Statistiques
        cours_aujourd_hui = Cours.objects.filter(date=today).count()
        cours_semaine = Cours.objects.filter(date__gte=today, date__lte=today + timedelta(days=7)).count()
        
        print("📊 Statistiques:")
        print(f"   📅 Cours aujourd'hui: {cours_aujourd_hui}")
        print(f"   📅 Cours cette semaine: {cours_semaine}")
        print(f"   👨‍🏫 Enseignants avec cours: {Cours.objects.values('enseignant').distinct().count()}")
        print(f"   🏫 Classes avec cours: {Cours.objects.values('classe').distinct().count()}")
        print()
        
        # Vérifier que chaque enseignant a des cours
        print("👨‍🏫 Vérification des enseignants:")
        for enseignant in enseignants:
            cours_count = Cours.objects.filter(enseignant=enseignant).count()
            if cours_count > 0:
                print(f"   ✅ {enseignant.user.get_full_name()}: {cours_count} cours")
        else:
                print(f"   ⚠️  {enseignant.user.get_full_name()}: Aucun cours")
        
        print()
        print("💡 Maintenant les enseignants peuvent utiliser le système de scan QR code !")
        print("   Accédez à /enseignant/appels/ pour voir les cours du jour")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des cours: {e}")
        return False

def main():
    """Fonction principale"""
    success = create_test_courses()
    
    if success:
        print("\n🎯 Prochaines étapes:")
        print("   1. Connectez-vous en tant qu'enseignant")
        print("   2. Allez dans 'Mes Cours' ou 'Appels du jour'")
        print("   3. Cliquez sur 'Démarrer l\'appel' pour un cours")
        print("   4. Utilisez le scan QR code pour prendre les présences")
        print("\n🚀 Le système FaceTrack est prêt !")
    else:
        print("\n❌ Échec de la création des cours. Vérifiez la configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()
