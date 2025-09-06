# admin.py
from django.contrib import admin
from .models import (
    User, Classe, Matiere, Parent, Enseignant, Eleve,
    Cours, Presence, Notification
)
from django.shortcuts import redirect


# ============================
# UTILISATEURS
# ============================
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email")


# ============================
# CLASSE & MATIERE
# ============================
@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'cycle', 'annee_scolaire', 'capacite', 'date_creation')
    list_filter = ('cycle', 'annee_scolaire')
    search_fields = ('nom', 'annee_scolaire')


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ("nom", "code", "coefficient")
    search_fields = ("nom", "code")


# ============================
# PERSONNES
# ============================
@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__username", "user__first_name", "user__last_name")


@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__username", "user__first_name", "user__last_name")


@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = ("user", "classe")
    list_filter = ("classe",)
    search_fields = ("user__first_name", "user__last_name")


# ============================
# COURS & PRESENCE
# ============================
@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ("id",)  # Ajoute d'autres champs si présents dans ton modèle
    search_fields = ()


@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ("id",)  # Ajoute d'autres champs si présents dans ton modèle
    search_fields = ()


# ============================
# NOTIFICATION
# ============================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id",)  # Ajoute d'autres champs si présents dans ton modèle
    search_fields = ()


# Supprime ou adapte la vue suivante si inutile
def some_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
