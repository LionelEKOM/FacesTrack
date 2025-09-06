#!/usr/bin/env python
"""
Script simple pour tester le système d'email avec les utilisateurs existants
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

def test_email_simple():
    """Test simple du système d'envoi d'email"""
    print("🧪 Test simple du système d'envoi d'email")
    print("=" * 40)
    
    try:
        # Vérifier les utilisateurs existants
        eleves = Eleve.objects.all()
        parents = Parent.objects.all()
        
        print(f"📊 Élèves disponibles: {eleves.count()}")
        print(f"📊 Parents disponibles: {parents.count()}")
        
        if eleves.count() == 0:
            print("❌ Aucun élève trouvé")
            return False
            
        if parents.count() == 0:
            print("❌ Aucun parent trouvé")
            return False
        
        # Prendre le premier élève et le premier parent
        eleve = eleves.first()
        parent = parents.first()
        
        # Associer le parent à l'élève
        eleve.parent = parent
        eleve.save()
        
        print(f"👤 Élève: {eleve.user.get_full_name()}")
        print(f"👨‍👩‍👧‍👦 Parent: {parent.user.get_full_name()} ({parent.user.email})")
        
        # Créer une classe et matière de test
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
            username='test_enseignant_email',
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
        
        # Créer un cours de test avec une date différente
        from datetime import timedelta
        cours_date = timezone.now().date() + timedelta(days=1)  # Demain
        
        cours, _ = Cours.objects.get_or_create(
            matiere=matiere,
            classe=classe,
            enseignant=enseignant,
            date=cours_date,
            heure_debut=time(10, 0),  # Heure différente
            defaults={
                'heure_fin': time(11, 0),
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
            presence.statut = 'PRESENT'
            presence.heure_arrivee = timezone.now().time()
            presence.methode_detection = 'QR_CODE'
            presence.save()
        
        print(f"✅ Présence créée: {presence.get_statut_display()}")
        
        # Tester l'envoi d'email de confirmation de présence
        print("\n📧 Test d'envoi d'email de confirmation de présence...")
        success = ParentNotificationService.send_presence_confirmation_email(presence.id)
        
        if success:
            print("✅ Email de confirmation envoyé avec succès!")
        else:
            print("❌ Échec de l'envoi de l'email")
        
        print("\n🎉 Test terminé!")
        print("📧 En mode DEBUG, l'email devrait apparaître dans la console Django")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_email_simple()
    sys.exit(0 if success else 1)
