#!/usr/bin/env python3
"""
Script de régénération des QR codes avec URLs de redirection mobile
Génère des QR codes contenant l'URL de redirection vers la page mobile check-in
"""

import os
import django
import qrcode
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceTrack.settings')
django.setup()

from school.models import Eleve
from django.conf import settings

def generate_qr_code_with_url(eleve_id, matricule, filename):
    """Génère une image QR code avec URL de redirection et la sauvegarde"""
    try:
        # Construire l'URL de redirection mobile
        # Note: Les paramètres cours_id et session_id seront ajoutés dynamiquement
        # lors de l'utilisation du QR code
        mobile_url = f"http://localhost:8000/mobile-checkin/{eleve_id}/COURS_ID/SESSION_ID/"
        
        # Créer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(mobile_url)
        qr.make(fit=True)
        
        # Créer l'image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Créer le dossier s'il n'existe pas
        qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes_eleves')
        os.makedirs(qr_dir, exist_ok=True)
        
        # Chemin complet du fichier
        file_path = os.path.join(qr_dir, filename)
        
        # Sauvegarder l'image
        img.save(file_path, format='PNG')
        
        return file_path
    except Exception as e:
        print(f"❌ Erreur lors de la génération du QR code pour {matricule}: {e}")
        return None

def regenerate_qr_codes_with_urls():
    """Régénère les QR codes avec URLs de redirection pour tous les élèves"""
    print("🚀 Début de la régénération des QR codes avec URLs de redirection...")
    print("=" * 80)
    
    # Récupérer tous les élèves
    eleves = Eleve.objects.select_related('user', 'classe').all()
    total_eleves = eleves.count()
    
    if total_eleves == 0:
        print("❌ Aucun élève trouvé dans la base de données.")
        return
    
    print(f"📚 Total d'élèves trouvés: {total_eleves}")
    print()
    
    # Statistiques
    qr_codes_generes = 0
    qr_codes_existants = 0
    erreurs = 0
    
    # Parcourir tous les élèves
    for i, eleve in enumerate(eleves, 1):
        eleve_id = eleve.id
        matricule = eleve.matricule
        nom_eleve = eleve.user.get_full_name()
        classe = eleve.classe.nom
        
        print(f"[{i:3d}/{total_eleves}] {nom_eleve} - {classe} - {matricule}")
        
        # Nom du fichier QR code
        qr_filename = f"QR_{matricule}.png"
        qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes_eleves')
        qr_path = os.path.join(qr_dir, qr_filename)
        
        # Supprimer l'ancien QR code s'il existe
        if os.path.exists(qr_path):
            os.remove(qr_path)
            print(f"    🗑️  Ancien QR code supprimé: {qr_filename}")
        
        # Générer le nouveau QR code avec URL
        qr_path = generate_qr_code_with_url(eleve_id, matricule, qr_filename)
        
        if qr_path:
            print(f"    🎯 Nouveau QR code généré avec URL: {qr_filename}")
            qr_codes_generes += 1
        else:
            print(f"    ❌ Échec de génération du QR code")
            erreurs += 1
    
    # Résumé final
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DE LA RÉGÉNÉRATION")
    print("=" * 80)
    print(f"✅ QR codes régénérés avec URLs: {qr_codes_generes}")
    print(f"❌ Erreurs: {erreurs}")
    print(f"📁 Dossier: {os.path.join(settings.MEDIA_ROOT, 'qr_codes_eleves')}")
    print()
    print("🎯 Les QR codes contiennent maintenant l'URL de redirection mobile!")
    print("📱 Format: http://localhost:8000/mobile-checkin/{eleve_id}/COURS_ID/SESSION_ID/")
    print("⚠️  Note: COURS_ID et SESSION_ID seront remplacés dynamiquement lors de l'utilisation")

if __name__ == "__main__":
    regenerate_qr_codes_with_urls()
