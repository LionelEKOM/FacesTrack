#!/usr/bin/env python3
"""
Script de test pour le système de QR Code FaceTrack
Ce script teste la génération et la lecture de QR codes
"""

import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceTrack.settings')
django.setup()

from school.models import Eleve, User, Classe
import qrcode
from PIL import Image
import io
import base64

def test_qr_code_generation():
    """Test de génération de QR codes pour les élèves"""
    print("🧪 Test de génération de QR codes...")
    
    try:
        # Récupérer quelques élèves de test
        eleves = Eleve.objects.all()[:3]
        
        if not eleves:
            print("❌ Aucun élève trouvé dans la base de données")
            return False
        
        for eleve in eleves:
            print(f"\n📱 Génération du QR code pour {eleve.user.get_full_name()}")
            print(f"   Matricule: {eleve.matricule}")
            
            # Générer le QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(eleve.matricule)
            qr.make(fit=True)
            
            # Créer l'image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Sauvegarder temporairement
            filename = f"test_qr_{eleve.matricule}.png"
            img.save(filename)
            print(f"   ✅ QR code généré et sauvegardé: {filename}")
            
            # Test de lecture (simulation)
            print(f"   🔍 Contenu du QR code: {eleve.matricule}")
            
            # Nettoyer
            os.remove(filename)
        
        print("\n✅ Test de génération de QR codes réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de génération: {e}")
        return False

def test_qr_code_model_method():
    """Test de la méthode get_qr_code_base64 du modèle Eleve"""
    print("\n🧪 Test de la méthode get_qr_code_base64...")
    
    try:
        eleve = Eleve.objects.first()
        if not eleve:
            print("❌ Aucun élève trouvé pour le test")
            return False
        
        print(f"📱 Test avec l'élève: {eleve.user.get_full_name()}")
        
        # Appeler la méthode
        qr_base64 = eleve.get_qr_code_base64()
        
        if qr_base64 and qr_base64.startswith('data:image/png;base64,'):
            print("   ✅ QR code base64 généré avec succès")
            print(f"   📏 Taille: {len(qr_base64)} caractères")
            
            # Décoder et vérifier
            try:
                base64_data = qr_base64.split(',')[1]
                image_data = base64.b64decode(base64_data)
                image = Image.open(io.BytesIO(image_data))
                print(f"   🖼️  Image décodée: {image.size[0]}x{image.size[1]} pixels")
                return True
            except Exception as e:
                print(f"   ❌ Erreur lors du décodage: {e}")
                return False
        else:
            print("   ❌ Format QR code base64 invalide")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test de la méthode: {e}")
        return False

def test_database_models():
    """Test des modèles de base de données"""
    print("\n🧪 Test des modèles de base de données...")
    
    try:
        # Test SessionAppel
        from school.models import SessionAppel
        print("   ✅ Modèle SessionAppel accessible")
        
        # Test Presence
        from school.models import Presence
        print("   ✅ Modèle Presence accessible")
        
        # Vérifier les choix de méthode
        methode_choices = SessionAppel._meta.get_field('methode').choices
        qr_code_choice = any(choice[0] == 'QR_CODE' for choice in methode_choices)
        
        if qr_code_choice:
            print("   ✅ Choix 'QR_CODE' disponible dans SessionAppel")
        else:
            print("   ❌ Choix 'QR_CODE' manquant dans SessionAppel")
            return False
        
        # Vérifier les choix de méthode_detection
        detection_choices = Presence._meta.get_field('methode_detection').choices
        qr_detection_choice = any(choice[0] == 'QR_CODE' for choice in detection_choices)
        
        if qr_detection_choice:
            print("   ✅ Choix 'QR_CODE' disponible dans Presence")
        else:
            print("   ❌ Choix 'QR_CODE' manquant dans Presence")
            return False
        
        print("   ✅ Test des modèles réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des modèles: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests du système QR Code FaceTrack")
    print("=" * 60)
    
    tests = [
        test_database_models,
        test_qr_code_generation,
        test_qr_code_model_method,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} a échoué avec une exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Résultats des tests: {passed}/{total} réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! Le système QR code est prêt.")
        return True
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
