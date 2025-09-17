#!/usr/bin/env python3
"""
Script de test pour la détection de visages avec une vraie image
"""

import cv2
import numpy as np
import os
import sys
from opencv_config import get_optimal_params, validate_image

def create_test_image_with_face():
    """Crée une image de test plus réaliste avec un visage"""
    # Créer une image de base
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Fond dégradé (corrigé pour éviter le dépassement)
    for y in range(480):
        for x in range(640):
            # Limiter les valeurs à 0-255
            value = min(255, max(0, 100 + y//3))
            img[y, x] = [value, value, value]
    
    # Dessiner un "visage" plus réaliste
    # Tête (ovale)
    center_x, center_y = 320, 240
    cv2.ellipse(img, (center_x, center_y), (120, 150), 0, 0, 360, (200, 200, 200), -1)
    
    # Yeux
    cv2.circle(img, (center_x - 40, center_y - 30), 15, (255, 255, 255), -1)
    cv2.circle(img, (center_x + 40, center_y - 30), 15, (255, 255, 255), -1)
    cv2.circle(img, (center_x - 40, center_y - 30), 8, (0, 0, 0), -1)
    cv2.circle(img, (center_x + 40, center_y - 30), 8, (0, 0, 0), -1)
    
    # Nez
    cv2.ellipse(img, (center_x, center_y), (8, 20), 0, 0, 180, (180, 180, 180), -1)
    
    # Bouche
    cv2.ellipse(img, (center_x, center_y + 40), (30, 15), 0, 0, 180, (150, 150, 150), -1)
    
    return img

def test_face_detection_with_real_image():
    """Teste la détection avec une image plus réaliste"""
    print("=== Test de détection avec image réaliste ===")
    
    # Créer l'image de test
    test_image = create_test_image_with_face()
    
    # Sauvegarder l'image de test
    cv2.imwrite('test_realistic_face.jpg', test_image)
    print("✓ Image de test créée: test_realistic_face.jpg")
    
    # Tester différents paramètres
    test_configs = [
        ('Sensible', 'sensitive'),
        ('Équilibré', 'balanced'),
        ('Conservateur', 'conservative')
    ]
    
    for config_name, config_type in test_configs:
        print(f"\n--- Test avec configuration {config_name} ---")
        
        # Obtenir les paramètres optimaux
        params = get_optimal_params(config_type)
        print(f"Paramètres: {params}")
        
        # Valider et optimiser l'image
        gray, validation_info = validate_image(test_image)
        print(f"Optimisations appliquées: {validation_info['optimizations_applied']}")
        
        # Charger le classificateur
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if face_cascade.empty():
            print("✗ Erreur: Impossible de charger le classificateur")
            continue
        
        # Détecter les visages
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=params['scaleFactor'],
            minNeighbors=params['minNeighbors'],
            minSize=params['minSize'],
            maxSize=params['maxSize']
        )
        
        print(f"Visages détectés: {len(faces)}")
        
        if len(faces) > 0:
            print("✓ Détection réussie!")
            for i, (x, y, w, h) in enumerate(faces):
                print(f"  Visage {i+1}: position=({x}, {y}), taille=({w}x{h})")
                
                # Dessiner le rectangle de détection
                result_img = test_image.copy()
                cv2.rectangle(result_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(result_img, f'Face {i+1}', (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                # Sauvegarder l'image avec détection
                output_filename = f'test_detection_{config_type}.jpg'
                cv2.imwrite(output_filename, result_img)
                print(f"  Image avec détection sauvegardée: {output_filename}")
        else:
            print("✗ Aucun visage détecté")
    
    return True

def test_with_webcam():
    """Teste la détection avec la webcam en temps réel"""
    print("\n=== Test avec webcam ===")
    
    # Essayer d'ouvrir la webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("✗ Impossible d'ouvrir la webcam")
        return False
    
    print("✓ Webcam ouverte avec succès")
    
    # Obtenir les propriétés de la webcam
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Résolution: {width}x{height}")
    print(f"FPS: {fps}")
    
    # Charger le classificateur
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    if face_cascade.empty():
        print("✗ Erreur: Impossible de charger le classificateur")
        cap.release()
        return False
    
    # Paramètres de détection
    params = get_optimal_params('balanced')
    
    print("Appuyez sur 'q' pour quitter, 's' pour sauvegarder une image")
    print("Détection en cours...")
    
    frame_count = 0
    faces_detected = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("✗ Erreur lors de la lecture de la webcam")
            break
        
        frame_count += 1
        
        # Traiter une image sur 3 pour la performance
        if frame_count % 3 != 0:
            continue
        
        # Convertir en niveaux de gris
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Améliorer le contraste
        gray = cv2.equalizeHist(gray)
        
        # Détecter les visages
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=params['scaleFactor'],
            minNeighbors=params['minNeighbors'],
            minSize=params['minSize'],
            maxSize=params['maxSize']
        )
        
        # Dessiner les rectangles de détection
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, 'Face', (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            faces_detected += 1
        
        # Afficher les informations
        cv2.putText(frame, f'Faces: {len(faces)}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Frame: {frame_count}', (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Afficher l'image
        cv2.imshow('Test Detection Visages - Webcam', frame)
        
        # Gérer les touches
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Sauvegarder l'image
            filename = f'webcam_detection_{frame_count}.jpg'
            cv2.imwrite(filename, frame)
            print(f"Image sauvegardée: {filename}")
    
    # Nettoyer
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\nTest terminé:")
    print(f"  Frames traitées: {frame_count}")
    print(f"  Visages détectés: {faces_detected}")
    
    return True

def main():
    """Fonction principale"""
    print("FaceTrack - Test de détection de visages avancé")
    print("=" * 60)
    
    try:
        # Test 1: Détection avec image réaliste
        test_face_detection_with_real_image()
        
        # Test 2: Détection avec webcam (optionnel)
        print("\n" + "=" * 60)
        response = input("Voulez-vous tester avec la webcam? (o/n): ").lower()
        
        if response in ['o', 'oui', 'y', 'yes']:
            test_with_webcam()
        else:
            print("Test webcam ignoré")
        
        print("\n" + "=" * 60)
        print("🎉 Tests terminés avec succès!")
        print("Vérifiez les images générées pour voir les résultats")
        
    except KeyboardInterrupt:
        print("\n\nTest interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
