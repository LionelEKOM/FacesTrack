# Guide de Dépannage - Reconnaissance Faciale FaceTrack

## Problèmes Courants et Solutions

### 1. Aucun visage détecté

#### Symptômes

- La caméra fonctionne mais aucun visage n'est détecté
- Messages d'erreur "Aucun visage détecté"
- Statistiques restent à 0 visages détectés

#### Causes possibles et solutions

**A. Problèmes d'éclairage**

- **Problème** : Éclairage insuffisant ou trop intense
- **Solution** :
  - Assurez-vous d'avoir un éclairage uniforme et suffisant
  - Évitez les ombres dures sur le visage
  - Évitez la contre-jour (fenêtre derrière le sujet)

**B. Position de la caméra**

- **Problème** : Caméra trop éloignée ou mal orientée
- **Solution** :
  - Placez la caméra à 50-150 cm du sujet
  - Assurez-vous que le visage occupe au moins 20% de l'image
  - Évitez les angles trop obliques

**C. Qualité de l'image**

- **Problème** : Résolution trop faible ou compression excessive
- **Solution** :
  - Utilisez une résolution minimale de 640x480
  - Vérifiez que la compression JPEG n'est pas trop agressive
  - Assurez-vous que l'autofocus de la caméra fonctionne

**D. Paramètres OpenCV trop stricts**

- **Problème** : Les paramètres de détection sont trop conservateurs
- **Solution** : Utilisez les paramètres optimisés dans `opencv_config.py`

### 2. Détection intermittente ou instable

#### Symptômes

- Visages détectés par intermittence
- Détection qui fonctionne puis s'arrête
- Faux positifs et faux négatifs

#### Solutions

**A. Ajuster les paramètres de détection**

```python
# Paramètres sensibles (plus de détections, plus de faux positifs)
params = {
    'scaleFactor': 1.02,
    'minNeighbors': 2,
    'minSize': (20, 20),
    'maxSize': (400, 400)
}

# Paramètres équilibrés (recommandé)
params = {
    'scaleFactor': 1.05,
    'minNeighbors': 3,
    'minSize': (30, 30),
    'maxSize': (300, 300)
}
```

**B. Optimiser le prétraitement d'image**

- Activer l'amélioration automatique du contraste
- Ajuster automatiquement la luminosité
- Utiliser l'égalisation d'histogramme

**C. Réduire la fréquence de capture**

- Augmenter l'intervalle entre les captures (2-3 secondes)
- Implémenter un système de cooldown

### 3. Erreurs OpenCV

#### Symptômes

- Messages d'erreur "Impossible de charger le classificateur"
- Erreurs de traitement d'image
- Plantages de l'application

#### Solutions

**A. Vérifier l'installation d'OpenCV**

```bash
# Installer OpenCV si nécessaire
pip install opencv-python
pip install opencv-contrib-python

# Vérifier l'installation
python -c "import cv2; print(cv2.__version__)"
```

**B. Vérifier les classificateurs Haar**

```bash
# Localiser les classificateurs
find /usr -name "haarcascade_frontalface_default.xml" 2>/dev/null
find /opt -name "haarcascade_frontalface_default.xml" 2>/dev/null
```

**C. Tester avec le script de diagnostic**

```bash
python test_opencv.py
```

### 4. Problèmes de performance

#### Symptômes

- Détection lente
- Interface qui se fige
- Utilisation CPU excessive

#### Solutions

**A. Optimiser la taille des images**

```python
# Redimensionner avant traitement
target_width = 640
target_height = 480
image = cv2.resize(image, (target_width, target_height))
```

**B. Réduire la fréquence de traitement**

```python
# Traiter une image sur 3
if frame_count % 3 == 0:
    process_frame()
```

**C. Utiliser le multithreading**

```python
import threading
from concurrent.futures import ThreadPoolExecutor

def process_frame_async(image_data):
    with ThreadPoolExecutor(max_workers=2) as executor:
        future = executor.submit(detect_faces, image_data)
        return future.result()
```

### 5. Problèmes de caméra

#### Symptômes

- Caméra ne se lance pas
- Erreur d'accès à la caméra
- Image de mauvaise qualité

#### Solutions

**A. Vérifier les permissions**

```bash
# Vérifier les groupes utilisateur
groups $USER

# Ajouter l'utilisateur au groupe video si nécessaire
sudo usermod -a -G video $USER
```

**B. Tester la caméra en ligne de commande**

```bash
# Installer v4l-utils
sudo apt install v4l-utils

# Lister les caméras disponibles
v4l2-ctl --list-devices

# Tester la caméra
ffplay /dev/video0
```

**C. Vérifier les pilotes**

```bash
# Vérifier les modules chargés
lsmod | grep uvcvideo

# Charger le module si nécessaire
sudo modprobe uvcvideo
```

## Tests de Diagnostic

### 1. Test OpenCV

```bash
python test_opencv.py
```

### 2. Test de la caméra

```bash
# Ouvrir la caméra avec Python
python -c "
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print('Caméra accessible')
    ret, frame = cap.read()
    if ret:
        print(f'Image capturée: {frame.shape}')
    cap.release()
else:
    print('Caméra non accessible')
"
```

### 3. Test de détection avec une image statique

```bash
# Créer une image de test
python -c "
import cv2
import numpy as np

# Créer une image avec un visage simulé
img = np.zeros((480, 640, 3), dtype=np.uint8)
cv2.rectangle(img, (200, 150), (440, 330), (255, 255, 255), -1)

# Sauvegarder l'image
cv2.imwrite('test_face.jpg', img)

# Tester la détection
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
faces = cascade.detectMultiScale(gray, 1.05, 3)

print(f'Visages détectés: {len(faces)}')
"
```

## Configuration Recommandée

### Paramètres optimaux pour la plupart des environnements

```python
FACE_DETECTION_CONFIG = {
    'scaleFactor': 1.05,
    'minNeighbors': 3,
    'minSize': (30, 30),
    'maxSize': (300, 300)
}
```

### Paramètres pour environnement difficile

```python
FACE_DETECTION_CONFIG = {
    'scaleFactor': 1.02,
    'minNeighbors': 2,
    'minSize': (20, 20),
    'maxSize': (400, 400)
}
```

### Paramètres pour environnement optimal

```python
FACE_DETECTION_CONFIG = {
    'scaleFactor': 1.1,
    'minNeighbors': 4,
    'minSize': (50, 50),
    'maxSize': (200, 200)
}
```

## Logs et Débogage

### Activer les logs détaillés

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Sauvegarder les images de débogage

```python
# Dans opencv_config.py
DEBUG_CONFIG = {
    'save_debug_images': True,
    'debug_image_path': '/tmp/facetrack_debug/'
}
```

## Support et Ressources

### Documentation officielle

- [OpenCV Face Detection](https://docs.opencv.org/4.x/d7/d8b/tutorial_py_face_detection.html)
- [Haar Cascade Classifiers](https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html)

### Communauté

- [OpenCV Forum](https://forum.opencv.org/)
- [Stack Overflow - OpenCV](https://stackoverflow.com/questions/tagged/opencv)

### Outils de diagnostic

- `test_opencv.py` - Test complet d'OpenCV
- `opencv_config.py` - Configuration optimisée
- Scripts de test intégrés dans l'interface

## Conclusion

La plupart des problèmes de détection faciale peuvent être résolus en :

1. Vérifiant l'installation d'OpenCV
2. Optimisant les paramètres de détection
3. Améliorant les conditions d'éclairage et de positionnement
4. Utilisant les outils de diagnostic fournis

Si les problèmes persistent, consultez les logs détaillés et utilisez les scripts de test pour identifier la cause exacte.
