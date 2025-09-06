#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FaceTrack.settings')
django.setup()

from school.models import Cours, Enseignant
from django.utils import timezone

# Vérifier les cours d'aujourd'hui
cours_aujourd_hui = Cours.objects.filter(date=timezone.now().date())
print(f'Cours aujourd\'hui: {cours_aujourd_hui.count()}')

for cours in cours_aujourd_hui:
    print(f'- {cours.matiere.nom} - {cours.classe.nom} ({cours.heure_debut} - {cours.heure_fin}) - Enseignant: {cours.enseignant.user.get_full_name()}')

# Vérifier les enseignants
enseignants = Enseignant.objects.all()
print(f'\nEnseignants disponibles: {enseignants.count()}')
for enseignant in enseignants:
    print(f'- {enseignant.user.get_full_name()} ({enseignant.user.username})')


