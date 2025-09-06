#!/usr/bin/env python
"""
Script pour ajouter des photos de référence aux élèves
"""
import os
import sys
import django
from django.core.files import File
from PIL import Image, ImageDraw, ImageFont
import io

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceTrack.settings')
django.setup()

from school.models import Eleve

def create_sample_photo(name, size=(400, 400)):
    """Créer une photo d'exemple avec le nom de l'élève"""
    # Créer une image avec un fond coloré
    img = Image.new('RGB', size, color=(70, 130, 180))  # Bleu acier
    
    # Ajouter du texte
    draw = ImageDraw.Draw(img)
    
    # Essayer de charger une police, sinon utiliser la police par défaut
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Centrer le texte
    bbox = draw.textbbox((0, 0), name, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Dessiner le texte
    draw.text((x, y), name, fill=(255, 255, 255), font=font)
    
    return img

def add_sample_photos():
    """Ajouter des photos de référence aux élèves qui n'en ont pas"""
    
    eleves = Eleve.objects.all()
    photos_ajoutees = 0
    
    for eleve in eleves:
        if not eleve.photo_reference:
            try:
                # Créer une photo d'exemple
                nom_complet = f"{eleve.user.first_name} {eleve.user.last_name}"
                photo = create_sample_photo(nom_complet)
                
                # Sauvegarder l'image en mémoire
                img_io = io.BytesIO()
                photo.save(img_io, format='JPEG', quality=85)
                img_io.seek(0)
                
                # Créer le nom de fichier
                filename = f"photo_{eleve.user.username}.jpg"
                
                # Sauvegarder dans le modèle
                eleve.photo_reference.save(filename, File(img_io), save=True)
                
                print(f"✅ Photo ajoutée pour {nom_complet}")
                photos_ajoutees += 1
                
            except Exception as e:
                print(f"❌ Erreur pour {eleve.user.get_full_name()}: {e}")
    
    print(f"\n📸 {photos_ajoutees} photos de référence ajoutées")
    return photos_ajoutees

if __name__ == '__main__':
    print("🖼️  Ajout de photos de référence aux élèves...")
    add_sample_photos()
    print("✅ Terminé !")
