#!/usr/bin/env python
"""
Script de test pour le système d'envoi d'email aux parents
"""
import os
import sys
import django
from datetime import datetime, time

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceTrack.settings')
django.setup()

from school.models import User, Eleve, Parent, Classe, Matiere, Enseignant, Cours, SessionAppel, Presence
from school.email_service import ParentNotificationService
from django.utils import timezone

def test_email_notifications():
    """Test du système d'envoi d'email aux parents"""
    print("🧪 Test du système d'envoi d'email aux parents")
    print("=" * 50)
    
    try:
        # Vérifier qu'il y a des élèves avec des parents
        eleves_avec_parents = Eleve.objects.filter(parent__isnull=False).select_related(
            'user', 'parent__user', 'classe'
        )
        
        if not eleves_avec_parents.exists():
            print("❌ Aucun élève avec parent trouvé dans la base de données")
            print("💡 Créez d'abord des utilisateurs de test avec create_realistic_users.py")
            return False
        
        # Prendre le premier élève avec parent
        eleve = eleves_avec_parents.first()
        print(f"👤 Élève sélectionné: {eleve.user.get_full_name()}")
        print(f"👨‍👩‍👧‍👦 Parent: {eleve.parent.user.get_full_name()} ({eleve.parent.user.email})")
        
        # Créer une classe et matière de test si nécessaire
        classe, _ = Classe.objects.get_or_create(
            nom='6A',
            defaults={'cycle': 'PREMIER', 'annee_scolaire': '2024-2025'}
        )
        
        matiere, _ = Matiere.objects.get_or_create(
            nom='Mathématiques',
            defaults={'description': 'Mathématiques de base'}
        )
        
        # Créer un enseignant de test
        enseignant_user, _ = User.objects.get_or_create(
            username='test_enseignant',
            defaults={
                'email': 'enseignant@test.com',
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'role': 'ENSEIGNANT'
            }
        )
        
        enseignant, _ = Enseignant.objects.get_or_create(
            user=enseignant_user,
            defaults={'date_embauche': timezone.now().date()}
        )
        enseignant.matieres.add(matiere)
        enseignant.classes.add(classe)
        
        # Créer un cours de test
        cours, _ = Cours.objects.get_or_create(
            matiere=matiere,
            classe=classe,
            enseignant=enseignant,
            date=timezone.now().date(),
            heure_debut=time(8, 0),
            defaults={
                'heure_fin': time(9, 0),
                'salle': 'Salle 101'
            }
        )
        
        # Créer une session d'appel de test
        session_appel, _ = SessionAppel.objects.get_or_create(
            cours=cours,
            enseignant=enseignant,
            defaults={
                'statut': 'EN_COURS',
                'methode': 'QR_CODE'
            }
        )
        
        print(f"📚 Cours: {cours.matiere.nom} - {cours.classe.nom}")
        print(f"📅 Date: {cours.date.strftime('%d/%m/%Y')}")
        print(f"⏰ Horaire: {cours.heure_debut.strftime('%H:%M')} - {cours.heure_fin.strftime('%H:%M')}")
        print(f"👨‍🏫 Enseignant: {enseignant.user.get_full_name()}")
        
        # Créer une présence de test
        presence, created = Presence.objects.get_or_create(
            eleve=eleve,
            session_appel=session_appel,
            defaults={
                'statut': 'PRESENT',
                'heure_arrivee': timezone.now().time(),
                'methode_detection': 'QR_CODE'
            }
        )
        
        if not created:
            # Mettre à jour la présence existante
            presence.statut = 'PRESENT'
            presence.heure_arrivee = timezone.now().time()
            presence.methode_detection = 'QR_CODE'
            presence.save()
        
        print(f"✅ Présence créée/mise à jour: {presence.get_statut_display()}")
        print(f"🕐 Heure d'arrivée: {presence.heure_arrivee.strftime('%H:%M')}")
        
        # Tester l'envoi d'email de confirmation de présence
        print("\n📧 Test d'envoi d'email de confirmation de présence...")
        success = ParentNotificationService.send_presence_confirmation_email(presence.id)
        
        if success:
            print("✅ Email de confirmation de présence envoyé avec succès!")
        else:
            print("❌ Échec de l'envoi de l'email de confirmation")
        
        # Tester l'envoi d'email de notification de retard
        print("\n📧 Test d'envoi d'email de notification de retard...")
        presence.statut = 'RETARD'
        presence.save()
        
        success = ParentNotificationService.send_retard_notification_email(presence.id)
        
        if success:
            print("✅ Email de notification de retard envoyé avec succès!")
        else:
            print("❌ Échec de l'envoi de l'email de retard")
        
        # Tester l'envoi d'email de notification d'absence
        print("\n📧 Test d'envoi d'email de notification d'absence...")
        presence.statut = 'ABSENT'
        presence.heure_arrivee = None
        presence.save()
        
        success = ParentNotificationService.send_absence_notification_email(presence.id)
        
        if success:
            print("✅ Email de notification d'absence envoyé avec succès!")
        else:
            print("❌ Échec de l'envoi de l'email d'absence")
        
        print("\n🎉 Tests terminés!")
        print("\n📋 Résumé:")
        print("- En mode DEBUG, les emails sont affichés dans la console")
        print("- En production, configurez les paramètres SMTP dans settings.py")
        print("- Vérifiez que les parents ont des adresses email valides")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

if __name__ == '__main__':
    success = test_email_notifications()
    sys.exit(0 if success else 1)
