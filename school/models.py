# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.timezone import now
import uuid

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('ENSEIGNANT', 'Teacher'),
        ('ELEVE', 'Student'),
        ('PARENT', 'Parent'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ELEVE')
    date_naissance = models.DateField(null=True, blank=True)
    adresse = models.TextField(blank=True)
    telephone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

class Classe(models.Model):
    CLASSE_CHOICES = [
        ('6A', '6th A'), ('6B', '6th B'),
        ('5A', '5th A'), ('5B', '5th B'),
        ('4A', '4th A'), ('4B', '4th B'),
        ('3A', '3rd A'), ('3B', '3rd B'),
        ('2ND', '10th'),
        ('1ERE', '11th'),
        ('TLE', '12th'),
    ]

    CYCLE_CHOICES = [
        ('PREMIER', 'First cycle (6th → 3rd)'),
        ('SECOND', 'Second cycle (10th → 12th)'),
    ]

    nom = models.CharField(max_length=10, choices=CLASSE_CHOICES)
    cycle = models.CharField(max_length=10, choices=CYCLE_CHOICES, default='PREMIER')  # 👈 default ajouté
    annee_scolaire = models.CharField(max_length=9, null=True, blank=True)  # ex: "2023-2024"
    capacite = models.IntegerField(default=30)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_nom_display()} - {self.get_cycle_display()} ({self.annee_scolaire})"

class Matiere(models.Model):
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, editable=False)  # généré automatiquement
    description = models.TextField(blank=True)
    coefficient = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    def save(self, *args, **kwargs):
        if not self.code:  # génère seulement au moment de la création
            # Génère un code du type MAT-XXXX
            unique_part = uuid.uuid4().hex[:4].upper()
            self.code = f"MAT-{unique_part}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} ({self.code})"

class Eleve(models.Model):
    def get_qr_code_base64(self):
        import qrcode
        import base64
        from io import BytesIO
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.matricule)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    classe = models.ForeignKey('Classe', on_delete=models.CASCADE)
    matricule = models.CharField(max_length=30, unique=True, editable=False)  # 👈 non éditable
    photo_reference = models.ImageField(
        upload_to='photos_eleves/', 
        null=True, 
        blank=True,
        help_text="4x4 square photo for facial recognition"
    )
    date_inscription = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('Parent', on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.matricule:
            annee = now().year  # ex: 2025
            id_classe = self.classe.id if self.classe else "X"
            code_unique = uuid.uuid4().hex[:4].upper()  # 4 caractères aléatoires
            self.matricule = f"{annee}-{id_classe}-{code_unique}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.matricule}"

class Enseignant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matieres = models.ManyToManyField(Matiere)
    classes = models.ManyToManyField(Classe)
    date_embauche = models.DateField()
    specialite = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {', '.join([m.nom for m in self.matieres.all()])}"

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profession = models.CharField(max_length=100, blank=True)
    lieu_travail = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - Parent"

class Cours(models.Model):
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    salle = models.CharField(max_length=20, blank=True)
    statut = models.CharField(max_length=20, choices=[
        ('PLANIFIE', 'Scheduled'),
        ('EN_COURS', 'In Progress'),
        ('TERMINE', 'Completed'),
        ('ANNULE', 'Cancelled')
    ], default='PLANIFIE')
    
    class Meta:
        unique_together = ['classe', 'date', 'heure_debut']

    def __str__(self):
        return f"{self.matiere.nom} - {self.classe.nom} - {self.date} {self.heure_debut}"

class SessionAppel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=[
        ('EN_COURS', 'In Progress'),
        ('TERMINE', 'Completed'),
        ('ANNULE', 'Cancelled')
    ], default='EN_COURS')
    methode = models.CharField(max_length=20, choices=[
        ('FACIAL', 'Facial Recognition'),
        ('QR_CODE', 'QR Code Scan'),
        ('MANUEL', 'Manual'),
        ('MIXTE', 'Mixed')
    ], default='QR_CODE')
    
    def __str__(self):
        return f"Session {self.id} - {self.cours} - {self.date_debut.strftime('%d/%m/%Y %H:%M')}"

class Presence(models.Model):
    STATUT_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('RETARD', 'Late'),
        ('JUSTIFIE', 'Justified')
    ]
    
    session_appel = models.ForeignKey(SessionAppel, on_delete=models.CASCADE)
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ABSENT')
    heure_arrivee = models.TimeField(null=True, blank=True)
    methode_detection = models.CharField(max_length=20, choices=[
        ('FACIAL', 'Facial Recognition'),
        ('MANUEL', 'Manual'),
        ('QR_CODE', 'QR Code')
    ], default='MANUEL')
    niveau_confiance = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    photo_capture = models.ImageField(upload_to='captures_presence/', null=True, blank=True)
    commentaire = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['session_appel', 'eleve']

    def __str__(self):
        return f"{self.eleve.user.get_full_name()} - {self.get_statut_display()} - {self.session_appel.cours.date}"

class Notification(models.Model):
    TYPE_CHOICES = [
        ('ABSENCE', 'Absence'),
        ('RETARD', 'Late'),
        ('PRESENCE', 'Attendance'),
        ('SYSTEME', 'System')
    ]
    
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    type_notification = models.CharField(max_length=20, choices=TYPE_CHOICES)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_lecture = models.DateTimeField(null=True, blank=True)
    lien = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"Notif {self.type_notification} - {self.date_creation.strftime('%d/%m/%Y %H:%M')}"

class PhotoReference(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photos_reference/')
    date_ajout = models.DateTimeField(auto_now_add=True)
    qualite = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], default=0.8)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Photo référence {self.eleve.user.get_full_name()} - {self.date_ajout.strftime('%d/%m/%Y')}"

class HistoriquePresence(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=Presence.STATUT_CHOICES)
    date = models.DateField()
    heure_arrivee = models.TimeField(null=True, blank=True)
    methode_detection = models.CharField(max_length=20, choices=Presence.methode_detection.field.choices)
    commentaire = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['eleve', 'cours', 'date']

    def __str__(self):
        return f"{self.eleve.user.get_full_name()} - {self.cours.matiere.nom} - {self.date} - {self.get_statut_display()}"

class Feedback(models.Model):
    TYPE_CHOICES = [
        ('GENERAL', 'General Question'),
        ('ABSENCE', 'Absence Justification'),
        ('RETARD', 'Delay Explanation'),
        ('COMPORTEMENT', 'Behavior Concern'),
        ('ACADEMIQUE', 'Academic Question'),
        ('TECHNIQUE', 'Technical Issue'),
        ('AUTRE', 'Other')
    ]
    
    STATUT_CHOICES = [
        ('NOUVEAU', 'New'),
        ('EN_COURS', 'In Progress'),
        ('REPONDU', 'Answered'),
        ('FERME', 'Closed')
    ]
    
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, null=True, blank=True)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, null=True, blank=True)
    type_feedback = models.CharField(max_length=20, choices=TYPE_CHOICES, default='GENERAL')
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='NOUVEAU')
    priorite = models.CharField(max_length=10, choices=[
        ('FAIBLE', 'Low'),
        ('NORMALE', 'Normal'),
        ('HAUTE', 'High'),
        ('URGENTE', 'Urgent')
    ], default='NORMALE')
    
    # Réponse de l'enseignant/administration
    reponse = models.TextField(blank=True)
    reponse_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks_repondus')
    date_reponse = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Feedback #{self.id} - {self.parent.user.get_full_name()} - {self.sujet}"
    
    @property
    def is_answered(self):
        return self.statut == 'REPONDU' and self.reponse
