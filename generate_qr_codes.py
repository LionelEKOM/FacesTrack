#!/usr/bin/env python3
"""
Script pour générer des QR codes pour tous les élèves FaceTrack
Ce script crée des QR codes PNG pour chaque élève basé sur leur matricule
"""

import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceTrack.settings')
django.setup()

from school.models import Eleve
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

def create_qr_code_directory():
    """Crée le répertoire pour stocker les QR codes"""
    qr_dir = "qr_codes_eleves"
    if not os.path.exists(qr_dir):
        os.makedirs(qr_dir)
        print(f"📁 Répertoire créé: {qr_dir}")
    return qr_dir

def generate_qr_code_for_student(eleve, qr_dir):
    """Génère un QR code pour un élève spécifique"""
    try:
        # Créer le QR code
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
        
        # Redimensionner pour une meilleure lisibilité
        img = img.resize((400, 400), Image.Resampling.NEAREST)
        
        # Créer une image plus grande avec des informations
        final_img = Image.new('RGB', (500, 600), 'white')
        draw = ImageDraw.Draw(final_img)
        
        # Coller le QR code
        final_img.paste(img, (50, 50))
        
        # Ajouter des informations textuelles
        try:
            # Essayer d'utiliser une police système
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 16)
        except:
            # Fallback sur la police par défaut
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Nom de l'élève
        draw.text((250, 470), eleve.user.get_full_name(), fill='black', anchor='mm', font=font_large)
        
        # Matricule
        draw.text((250, 500), f"Matricule: {eleve.matricule}", fill='black', anchor='mm', font=font_small)
        
        # Classe
        draw.text((250, 525), f"Classe: {eleve.classe.nom}", fill='black', anchor='mm', font=font_small)
        
        # Date de génération
        from datetime import datetime
        date_str = datetime.now().strftime("%d/%m/%Y")
        draw.text((250, 550), f"Généré le: {date_str}", fill='gray', anchor='mm', font=font_small)
        
        # Ajouter un logo ou titre
        draw.text((250, 20), "FaceTrack - QR Code Élève", fill='#007bff', anchor='mm', font=font_large)
        
        # Sauvegarder
        filename = f"QR_{eleve.matricule}_{eleve.user.last_name}_{eleve.user.first_name}.png"
        filename = filename.replace(" ", "_").replace("-", "_")
        filepath = os.path.join(qr_dir, filename)
        
        final_img.save(filepath, "PNG", quality=95)
        
        return filepath, True
        
    except Exception as e:
        print(f"   ❌ Erreur lors de la génération du QR code pour {eleve.user.get_full_name()}: {e}")
        return None, False

def main():
    """Fonction principale"""
    print("🚀 Génération des QR codes pour tous les élèves FaceTrack")
    print("=" * 70)
    
    # Créer le répertoire
    qr_dir = create_qr_code_directory()
    
    # Récupérer tous les élèves
    eleves = Eleve.objects.all().order_by('classe__nom', 'user__last_name', 'user__first_name')
    
    if not eleves:
        print("❌ Aucun élève trouvé dans la base de données")
        return
    
    print(f"📚 {eleves.count()} élève(s) trouvé(s)")
    print()
    
    # Statistiques par classe
    classes_count = {}
    for eleve in eleves:
        classe_nom = eleve.classe.nom
        classes_count[classe_nom] = classes_count.get(classe_nom, 0) + 1
    
    print("📊 Répartition par classe:")
    for classe, count in sorted(classes_count.items()):
        print(f"   {classe}: {count} élève(s)")
    print()
    
    # Générer les QR codes
    success_count = 0
    error_count = 0
    
    for i, eleve in enumerate(eleves, 1):
        print(f"[{i:2d}/{len(eleves)}] 📱 Génération pour {eleve.user.get_full_name()}")
        print(f"      Classe: {eleve.classe.nom} | Matricule: {eleve.matricule}")
        
        filepath, success = generate_qr_code_for_student(eleve, qr_dir)
        
        if success:
            print(f"      ✅ QR code généré: {os.path.basename(filepath)}")
            success_count += 1
        else:
            print(f"      ❌ Échec de la génération")
            error_count += 1
        
        print()
    
    # Résumé
    print("=" * 70)
    print("📊 Résumé de la génération:")
    print(f"   ✅ Succès: {success_count}")
    print(f"   ❌ Échecs: {error_count}")
    print(f"   📁 Répertoire: {qr_dir}")
    
    if success_count > 0:
        print(f"\n🎉 {success_count} QR code(s) généré(s) avec succès !")
        print(f"📂 Les fichiers sont disponibles dans le répertoire: {qr_dir}")
        
        # Lister quelques fichiers générés
        files = os.listdir(qr_dir)
        if files:
            print(f"\n📋 Exemples de fichiers générés:")
            for file in sorted(files)[:5]:
                print(f"   • {file}")
            if len(files) > 5:
                print(f"   ... et {len(files) - 5} autres")
    
    if error_count > 0:
        print(f"\n⚠️  {error_count} erreur(s) rencontrée(s). Vérifiez les logs ci-dessus.")
    
    print("\n💡 Conseil: Imprimez ces QR codes et distribuez-les aux élèves")
    print("   ou utilisez-les avec l'interface de scan QR de FaceTrack !")

if __name__ == "__main__":
    main()
