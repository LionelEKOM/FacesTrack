#!/usr/bin/env python3
"""
Script de génération des QR codes pour tous les élèves FaceTrack
Génère et sauvegarde les QR codes basés sur les matricules des élèves
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

def generate_qr_code_image(matricule, filename):
    """Génère une image QR code et la sauvegarde"""
    try:
        # Créer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(matricule)
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

def generate_qr_codes_for_all_students():
    """Génère les QR codes pour tous les élèves"""
    print("🚀 Début de la génération des QR codes pour tous les élèves...")
    print("=" * 70)
    
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
        matricule = eleve.matricule
        nom_eleve = eleve.user.get_full_name()
        classe = eleve.classe.nom
        
        print(f"[{i:3d}/{total_eleves}] {nom_eleve} - {classe} - {matricule}")
        
        # Vérifier si le QR code existe déjà
        qr_filename = f"QR_{matricule}.png"
        qr_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes_eleves')
        qr_path = os.path.join(qr_dir, qr_filename)
        
        if os.path.exists(qr_path):
            print(f"    ✅ QR code déjà existant: {qr_filename}")
            qr_codes_existants += 1
            continue
        
        # Générer le QR code
        qr_path = generate_qr_code_image(matricule, qr_filename)
        
        if qr_path:
            print(f"    🎯 QR code généré: {qr_filename}")
            qr_codes_generes += 1
        else:
            print(f"    ❌ Échec de génération du QR code")
            erreurs += 1
    
    # Résumé final
    print("\n" + "=" * 70)
    print("🎉 GÉNÉRATION DES QR CODES TERMINÉE !")
    print("=" * 70)
    print(f"📊 Statistiques:")
    print(f"  • Total d'élèves: {total_eleves}")
    print(f"  • QR codes générés: {qr_codes_generes}")
    print(f"  • QR codes existants: {qr_codes_existants}")
    print(f"  • Erreurs: {erreurs}")
    print(f"  • Total QR codes: {qr_codes_generes + qr_codes_existants}")
    
    if qr_codes_generes > 0:
        print(f"\n📁 QR codes sauvegardés dans: {os.path.join(settings.MEDIA_ROOT, 'qr_codes_eleves')}")
        print(f"🔗 URL d'accès: /media/qr_codes_eleves/")
    
    print(f"\n⚠️  Note: Les QR codes contiennent le matricule de l'élève pour l'identification")

def generate_qr_code_for_specific_student(matricule):
    """Génère un QR code pour un élève spécifique"""
    try:
        eleve = Eleve.objects.get(matricule=matricule)
        nom_eleve = eleve.user.get_full_name()
        classe = eleve.classe.nom
        
        print(f"🎯 Génération du QR code pour: {nom_eleve} - {classe} - {matricule}")
        
        qr_filename = f"QR_{matricule}.png"
        qr_path = generate_qr_code_image(matricule, qr_filename)
        
        if qr_path:
            print(f"✅ QR code généré avec succès: {qr_filename}")
            print(f"📁 Fichier sauvegardé: {qr_path}")
        else:
            print(f"❌ Échec de la génération du QR code")
            
    except Eleve.DoesNotExist:
        print(f"❌ Aucun élève trouvé avec le matricule: {matricule}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Fonction principale"""
    import sys
    
    if len(sys.argv) > 1:
        # Si un matricule est fourni en argument, générer le QR code pour cet élève
        matricule = sys.argv[1]
        generate_qr_code_for_specific_student(matricule)
    else:
        # Sinon, générer les QR codes pour tous les élèves
        generate_qr_codes_for_all_students()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Génération interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
