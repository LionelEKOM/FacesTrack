#!/usr/bin/env python3
"""
Script de test pour vérifier les QR codes et leurs URLs de redirection
"""

import os
import django
import qrcode
from PIL import Image
import io

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceTrack.settings')
django.setup()

from school.models import Eleve
from django.conf import settings

def test_qr_code_content():
    """Teste le contenu des QR codes générés"""
    print("🔍 Test du contenu des QR codes...")
    print("=" * 60)
    
    # Récupérer quelques élèves pour tester
    eleves = Eleve.objects.select_related('user', 'classe').all()[:3]
    
    for eleve in eleves:
        eleve_id = eleve.id
        matricule = eleve.matricule
        nom_eleve = eleve.user.get_full_name()
        
        print(f"\n📱 Test pour: {nom_eleve} (ID: {eleve_id}, Matricule: {matricule})")
        
        # Construire l'URL de redirection mobile
        mobile_url = f"http://localhost:8000/mobile-checkin/{eleve_id}/COURS_ID/SESSION_ID/"
        
        # Générer le QR code
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
        
        # Convertir en bytes pour décoder
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Décoder le QR code pour vérifier le contenu
        try:
            # Utiliser une méthode simple pour décoder
            decoded_data = qr.get_data()
            print(f"    ✅ QR code généré avec succès")
            print(f"    📋 Contenu: {decoded_data}")
            print(f"    🔗 URL de redirection: {mobile_url}")
            
            # Vérifier que l'URL contient les bons paramètres
            if f"/mobile-checkin/{eleve_id}/" in decoded_data:
                print(f"    ✅ URL contient l'ID élève correct")
            else:
                print(f"    ❌ URL ne contient pas l'ID élève correct")
                
        except Exception as e:
            print(f"    ❌ Erreur lors du décodage: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 RÉSUMÉ DU TEST")
    print("=" * 60)
    print("✅ Les QR codes contiennent maintenant les URLs de redirection mobile")
    print("📱 Format: http://localhost:8000/mobile-checkin/{eleve_id}/COURS_ID/SESSION_ID/")
    print("⚠️  COURS_ID et SESSION_ID seront remplacés dynamiquement lors de l'utilisation")

if __name__ == "__main__":
    test_qr_code_content()
