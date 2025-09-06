from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Crée des utilisateurs de test pour chaque rôle"

    def handle(self, *args, **options):
        users = [
            {"username": "admin", "password": "admin123", "role": "ADMIN"},
            {"username": "teacher", "password": "teacher123", "role": "ENSEIGNANT"},
            {"username": "student", "password": "student123", "role": "ELEVE"},
            {"username": "parent", "password": "parent123", "role": "PARENT"},
        ]
        for u in users:
            if not User.objects.filter(username=u["username"]).exists():
                user = User.objects.create_user(
                    username=u["username"],
                    password=u["password"],
                    role=u["role"],
                    email=f"{u['username']}@test.com"
                )
                if u["role"] == "ADMIN":
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                self.stdout.write(self.style.SUCCESS(f"Utilisateur {u['username']} créé."))
            else:
                self.stdout.write(self.style.WARNING(f"Utilisateur {u['username']} existe déjà."))
