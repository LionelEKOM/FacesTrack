from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from .models import Eleve, Parent, Presence, Cours, SessionAppel
import logging

logger = logging.getLogger(__name__)

class ParentNotificationService:
    """
    Service pour envoyer des notifications par email aux parents
    """
    
    @staticmethod
    def send_presence_confirmation_email(presence_id):
        """
        Envoie un email de confirmation de présence au parent de l'élève
        
        Args:
            presence_id: ID de l'objet Presence
        """
        try:
            # Récupérer la présence avec toutes les informations nécessaires
            presence = Presence.objects.select_related(
                'eleve__user',
                'eleve__parent__user',
                'eleve__classe',
                'session_appel__cours__matiere',
                'session_appel__cours__enseignant__user'
            ).get(id=presence_id)
            
            # Vérifier que l'élève a un parent
            if not presence.eleve.parent:
                logger.warning(f"L'élève {presence.eleve.user.get_full_name()} n'a pas de parent associé")
                return False
            
            # Informations de base
            eleve = presence.eleve
            parent = presence.eleve.parent
            cours = presence.session_appel.cours
            enseignant = presence.session_appel.cours.enseignant
            
            # Préparer le contexte pour le template
            context = {
                'eleve_nom': eleve.user.get_full_name(),
                'parent_nom': parent.user.get_full_name(),
                'cours_matiere': cours.matiere.nom,
                'cours_classe': cours.classe.nom,
                'cours_date': cours.date.strftime('%d/%m/%Y'),
                'cours_heure': f"{cours.heure_debut.strftime('%H:%M')} - {cours.heure_fin.strftime('%H:%M')}",
                'cours_salle': cours.salle,
                'enseignant_nom': enseignant.user.get_full_name(),
                'presence_heure': presence.heure_arrivee.strftime('%H:%M') if presence.heure_arrivee else None,
                'presence_methode': presence.get_methode_detection_display(),
                'confirmation_date': timezone.now().strftime('%d/%m/%Y à %H:%M'),
                'ecole_nom': 'FaceTrack École',
                'ecole_email': settings.DEFAULT_FROM_EMAIL,
            }
            
            # Générer le contenu HTML de l'email
            html_message = render_to_string('emails/presence_confirmation.html', context)
            
            # Générer le contenu texte simple
            plain_message = strip_tags(html_message)
            
            # Sujet de l'email
            subject = f"✅ Présence confirmée - {eleve.user.first_name} {eleve.user.last_name} - {cours.matiere.nom}"
            
            # Envoyer l'email
            success = send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[parent.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            if success:
                logger.info(f"Email de confirmation envoyé avec succès à {parent.user.email} pour {eleve.user.get_full_name()}")
                return True
            else:
                logger.error(f"Échec de l'envoi de l'email à {parent.user.email}")
                return False
                
        except Presence.DoesNotExist:
            logger.error(f"Presence avec l'ID {presence_id} n'existe pas")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email de confirmation: {str(e)}")
            return False
    
    @staticmethod
    def send_absence_notification_email(presence_id):
        """
        Envoie un email de notification d'absence au parent de l'élève
        
        Args:
            presence_id: ID de l'objet Presence
        """
        try:
            # Récupérer la présence avec toutes les informations nécessaires
            presence = Presence.objects.select_related(
                'eleve__user',
                'eleve__parent__user',
                'eleve__classe',
                'session_appel__cours__matiere',
                'session_appel__cours__enseignant__user'
            ).get(id=presence_id)
            
            # Vérifier que l'élève a un parent
            if not presence.eleve.parent:
                logger.warning(f"L'élève {presence.eleve.user.get_full_name()} n'a pas de parent associé")
                return False
            
            # Informations de base
            eleve = presence.eleve
            parent = presence.eleve.parent
            cours = presence.session_appel.cours
            enseignant = presence.session_appel.cours.enseignant
            
            # Préparer le contexte pour le template
            context = {
                'eleve_nom': eleve.user.get_full_name(),
                'parent_nom': parent.user.get_full_name(),
                'cours_matiere': cours.matiere.nom,
                'cours_classe': cours.classe.nom,
                'cours_date': cours.date.strftime('%d/%m/%Y'),
                'cours_heure': f"{cours.heure_debut.strftime('%H:%M')} - {cours.heure_fin.strftime('%H:%M')}",
                'cours_salle': cours.salle,
                'enseignant_nom': enseignant.user.get_full_name(),
                'notification_date': timezone.now().strftime('%d/%m/%Y à %H:%M'),
                'ecole_nom': 'FaceTrack École',
                'ecole_email': settings.DEFAULT_FROM_EMAIL,
            }
            
            # Générer le contenu HTML de l'email
            html_message = render_to_string('emails/absence_notification.html', context)
            
            # Générer le contenu texte simple
            plain_message = strip_tags(html_message)
            
            # Sujet de l'email
            subject = f"⚠️ Absence signalée - {eleve.user.first_name} {eleve.user.last_name} - {cours.matiere.nom}"
            
            # Envoyer l'email
            success = send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[parent.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            if success:
                logger.info(f"Email d'absence envoyé avec succès à {parent.user.email} pour {eleve.user.get_full_name()}")
                return True
            else:
                logger.error(f"Échec de l'envoi de l'email d'absence à {parent.user.email}")
                return False
                
        except Presence.DoesNotExist:
            logger.error(f"Presence avec l'ID {presence_id} n'existe pas")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email d'absence: {str(e)}")
            return False
    
    @staticmethod
    def send_retard_notification_email(presence_id):
        """
        Envoie un email de notification de retard au parent de l'élève
        
        Args:
            presence_id: ID de l'objet Presence
        """
        try:
            # Récupérer la présence avec toutes les informations nécessaires
            presence = Presence.objects.select_related(
                'eleve__user',
                'eleve__parent__user',
                'eleve__classe',
                'session_appel__cours__matiere',
                'session_appel__cours__enseignant__user'
            ).get(id=presence_id)
            
            # Vérifier que l'élève a un parent
            if not presence.eleve.parent:
                logger.warning(f"L'élève {presence.eleve.user.get_full_name()} n'a pas de parent associé")
                return False
            
            # Informations de base
            eleve = presence.eleve
            parent = presence.eleve.parent
            cours = presence.session_appel.cours
            enseignant = presence.session_appel.cours.enseignant
            
            # Calculer le retard
            retard_minutes = None
            if presence.heure_arrivee and cours.heure_debut:
                from datetime import datetime, time
                heure_debut = datetime.combine(cours.date, cours.heure_debut)
                heure_arrivee = datetime.combine(cours.date, presence.heure_arrivee)
                retard_minutes = int((heure_arrivee - heure_debut).total_seconds() / 60)
            
            # Préparer le contexte pour le template
            context = {
                'eleve_nom': eleve.user.get_full_name(),
                'parent_nom': parent.user.get_full_name(),
                'cours_matiere': cours.matiere.nom,
                'cours_classe': cours.classe.nom,
                'cours_date': cours.date.strftime('%d/%m/%Y'),
                'cours_heure': f"{cours.heure_debut.strftime('%H:%M')} - {cours.heure_fin.strftime('%H:%M')}",
                'cours_salle': cours.salle,
                'enseignant_nom': enseignant.user.get_full_name(),
                'presence_heure': presence.heure_arrivee.strftime('%H:%M') if presence.heure_arrivee else None,
                'retard_minutes': retard_minutes,
                'notification_date': timezone.now().strftime('%d/%m/%Y à %H:%M'),
                'ecole_nom': 'FaceTrack École',
                'ecole_email': settings.DEFAULT_FROM_EMAIL,
            }
            
            # Générer le contenu HTML de l'email
            html_message = render_to_string('emails/retard_notification.html', context)
            
            # Générer le contenu texte simple
            plain_message = strip_tags(html_message)
            
            # Sujet de l'email
            subject = f"⏰ Retard signalé - {eleve.user.first_name} {eleve.user.last_name} - {cours.matiere.nom}"
            
            # Envoyer l'email
            success = send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[parent.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            if success:
                logger.info(f"Email de retard envoyé avec succès à {parent.user.email} pour {eleve.user.get_full_name()}")
                return True
            else:
                logger.error(f"Échec de l'envoi de l'email de retard à {parent.user.email}")
                return False
                
        except Presence.DoesNotExist:
            logger.error(f"Presence avec l'ID {presence_id} n'existe pas")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email de retard: {str(e)}")
            return False
