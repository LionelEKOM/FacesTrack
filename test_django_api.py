#!/usr/bin/env python3
"""
Script de test pour l'API Django de reconnaissance faciale
"""

import requests
import base64
import json
import cv2
import numpy as np
import os
import sys

def create_test_image():
    """Crée une image de test simple"""
    # Créer une image avec un visage simulé
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img[:] = (128, 128, 128)  # Fond gris
    
    # Dessiner un visage simple
    center_x, center_y = 320, 240
    cv2.circle(img, (center_x, center_y), 100, (200, 200, 200), -1)
    
    # Yeux
    cv2.circle(img, (center_x - 30, center_y - 20), 15, (255, 255, 255), -1)
    cv2.circle(img, (center_x + 30, center_y - 20), 15, (255, 255, 255), -1)
    
    return img

def image_to_base64(image):
    """Convertit une image numpy en base64"""
    # Encoder en JPEG
    _, buffer = cv2.imencode('.jpg', image)
    # Convertir en base64
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{jpg_as_text}"

def test_django_api():
    """Teste l'API Django de reconnaissance faciale"""
    print("=== Test de l'API Django ===")
    
    # Configuration
    base_url = "http://localhost:8000"  # Ajuster selon votre configuration
    api_endpoint = f"{base_url}/api/facial-recognition/"
    
    # Créer une image de test
    test_image = create_test_image()
    
    # Sauvegarder l'image de test
    cv2.imwrite('test_api_image.jpg', test_image)
    print("✓ Image de test créée: test_api_image.jpg")
    
    # Convertir en base64
    image_base64 = image_to_base64(test_image)
    print(f"✓ Image convertie en base64 ({len(image_base64)} caractères)")
    
    # Données de test
    test_data = {
        "session_id": 1,  # ID de session de test
        "image": image_base64
    }
    
    print(f"\nEnvoi de la requête à: {api_endpoint}")
    print("Données:", {k: v[:50] + "..." if k == "image" else v for k, v in test_data.items()})
    
    try:
        # Envoyer la requête
        response = requests.post(
            api_endpoint,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\nRéponse reçue:")
        print(f"  Status Code: {response.status_code}")
        print(f"  Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  Données JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if data.get('success'):
                    print("✓ API fonctionne correctement!")
                    if data.get('total_faces', 0) > 0:
                        print(f"  Visages détectés: {data['total_faces']}")
                        for face in data.get('detected_faces', []):
                            print(f"    - {face.get('name', 'Inconnu')} (confiance: {face.get('confidence', 0)})")
                    else:
                        print("  Aucun visage détecté (normal pour une image simulée)")
                else:
                    print("✗ API retourne une erreur:", data.get('error', 'Erreur inconnue'))
                    
            except json.JSONDecodeError as e:
                print(f"✗ Erreur de décodage JSON: {e}")
                print(f"  Contenu brut: {response.text[:200]}...")
                
        else:
            print(f"✗ Erreur HTTP: {response.status_code}")
            print(f"  Contenu: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("✗ Erreur de connexion: Impossible de se connecter au serveur Django")
        print("  Assurez-vous que le serveur Django est en cours d'exécution sur", base_url)
        
    except requests.exceptions.Timeout:
        print("✗ Erreur de timeout: La requête a pris trop de temps")
        
    except Exception as e:
        print(f"✗ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()

def test_with_real_image(image_path):
    """Teste avec une vraie image"""
    print(f"\n=== Test avec image réelle: {image_path} ===")
    
    if not os.path.exists(image_path):
        print(f"✗ Image non trouvée: {image_path}")
        return
    
    try:
        # Charger l'image
        image = cv2.imread(image_path)
        if image is None:
            print(f"✗ Impossible de charger l'image: {image_path}")
            return
        
        print(f"✓ Image chargée: {image.shape}")
        
        # Convertir en base64
        image_base64 = image_to_base64(image)
        
        # Données de test
        test_data = {
            "session_id": 1,
            "image": image_base64
        }
        
        # Envoyer la requête (simulation)
        print("✓ Image prête pour l'API")
        print(f"  Taille base64: {len(image_base64)} caractères")
        
        # Note: Ici on simule juste la préparation, l'envoi réel nécessite un serveur Django actif
        
    except Exception as e:
        print(f"✗ Erreur lors du traitement de l'image: {e}")

def main():
    """Fonction principale"""
    print("FaceTrack - Test de l'API Django de reconnaissance faciale")
    print("=" * 70)
    
    # Test 1: API Django
    test_django_api()
    
    # Test 2: Avec les images de test générées
    print("\n" + "=" * 70)
    print("Tests avec images de test générées:")
    
    test_images = [
        'test_realistic_face.jpg',
        'test_detection_balanced.jpg',
        'test_detection_sensitive.jpg'
    ]
    
    for img_path in test_images:
        if os.path.exists(img_path):
            test_with_real_image(img_path)
    
    print("\n" + "=" * 70)
    print("Résumé des tests:")
    print("✓ Images de test créées et prêtes")
    print("⚠️  Test API Django nécessite un serveur Django actif")
    print("\nPour tester complètement l'API:")
    print("1. Démarrer le serveur Django: python3 manage.py runserver")
    print("2. Ajuster l'URL dans le script si nécessaire")
    print("3. Relancer ce script de test")

if __name__ == "__main__":
    main()
