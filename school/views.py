from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
import numpy as np
import os
from PIL import Image
import base64
from .forms import LoginForm, FeedbackForm
from .models import User, Classe, Matiere, Eleve, Enseignant, Parent, Cours, SessionAppel, Presence, Notification, PhotoReference, HistoriquePresence, Feedback

"""
    This function is likely intended to display the classes taught by a teacher, and it requires the
    user to be logged in to access it.
    
    :param request: The `request` parameter in the `teacher_classes` function is an object that contains
    information about the current HTTP request. It includes details such as the user making the request,
    any data sent with the request, and other metadata related to the request. This parameter allows the
    function to access and interact with
"""
@login_required
def teacher_classes(request):
    """Vue pour afficher les classes de l'enseignant"""
    if request.user.role != 'ENSEIGNANT':
        messages.error(request, 'Access denied.')
        return redirect('login')
    
    try:
        enseignant = Enseignant.objects.get(user=request.user)
        
        # Récupérer les classes de l'enseignant
        classes = Classe.objects.filter(cours__enseignant=enseignant).distinct()
        
        # Statistiques par classe
        classes_with_stats = []
        for classe in classes:
            # Nombre d'élèves dans la classe
            nb_eleves = Eleve.objects.filter(classe=classe).count()
            
            # Nombre de cours de l'enseignant dans cette classe
            nb_cours = Cours.objects.filter(enseignant=enseignant, classe=classe).count()
            
            # Taux de présence moyen (dernière semaine)
            debut_semaine = timezone.now().date() - timedelta(days=7)
            presences_classe = Presence.objects.filter(
                session_appel__cours__classe=classe,
                session_appel__cours__enseignant=enseignant,
                session_appel__cours__date__gte=debut_semaine
            )
            
            total_presences = presences_classe.count()
            presences_validees = presences_classe.filter(statut__in=['PRESENT', 'RETARD']).count()
            taux_presence = round((presences_validees / total_presences * 100) if total_presences > 0 else 0, 1)
            
            classes_with_stats.append({
                'classe': classe,
                'nb_eleves': nb_eleves,
                'nb_cours': nb_cours,
                'taux_presence': taux_presence
            })
        
        context = {
            'enseignant': enseignant,
            'classes_with_stats': classes_with_stats,
        }
        
        return render(request, 'teacher_classes.html', context)
        
    except Enseignant.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('login')


@login_required
def admin_dashboard(request): 
    """
    This function likely renders an admin dashboard page in a web application based on the request
    received.
    
    :param request: The `request` parameter in the `admin_dashboard` function is typically an object
    that contains information about the current HTTP request. It includes details such as the user
    making the request, any data being sent with the request, and other metadata related to the request.
    This parameter allows the function to access and
    """
    """View of the complete admin dashboard"""
    if request.user.role != 'ADMIN':
        messages.error(request, 'Access denied. Administrator role required.')
        return redirect('login')
    
    try:
        # Statistiques du système
        total_students = User.objects.filter(role='ELEVE').count()
        total_teachers = User.objects.filter(role='ENSEIGNANT').count()
        total_parents = User.objects.filter(role='PARENT').count()
        total_admins = User.objects.filter(role='ADMIN').count()
        total_classes = Classe.objects.count()
        total_courses = Cours.objects.count()
        
        # Cours du jour
        aujourd_hui = timezone.now().date()
        cours_aujourd_hui = Cours.objects.filter(date=aujourd_hui).count()
        
        # Sessions d'appel en cours
        sessions_en_cours = SessionAppel.objects.filter(statut='EN_COURS').count()
        
        # Activités récentes
        recent_activities = []
        
        # Derniers cours créés
        derniers_cours = Cours.objects.select_related('matiere', 'classe', 'enseignant__user').order_by('-date')[:5]
        for cours in derniers_cours:
            recent_activities.append({
                'type': 'Cours',
                'description': f'{cours.matiere.nom} - {cours.classe.nom}',
                'time': cours.date.strftime('%d/%m'),
                'icon': 'fas fa-book',
                'color': 'primary'
            })
        
        # Derniers utilisateurs créés
        derniers_users = User.objects.order_by('-date_joined')[:3]
        for user in derniers_users:
            recent_activities.append({
                'type': 'Utilisateur',
                'description': f'{user.get_full_name()} ({user.get_role_display()})',
                'time': user.date_joined.strftime('%d/%m'),
                'icon': 'fas fa-user-plus',
                'color': 'success'
            })
        
        context = {
            'user': request.user,
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_parents': total_parents,
            'total_admins': total_admins,
            'total_classes': total_classes,
            'total_courses': total_courses,
            'cours_aujourd_hui': cours_aujourd_hui,
            'sessions_en_cours': sessions_en_cours,
            'recent_activities': recent_activities,
        }
        
        return render(request, 'dashboard_admin.html', context)
        
    except Exception as e:
        messages.error(request, f'Erreur lors du chargement du dashboard: {str(e)}')
        return redirect('login')

def home(request):
    """Vue d'accueil basique"""
    return HttpResponse("Welcome to FacesTrack!")

def login_view(request):
    """
    This function likely handles the view for user login in a web application.
    
    :param request: The `request` parameter in the `login_view` function is typically an HttpRequest
    object that represents the current HTTP request. It contains information about the request made by
    the client, such as the user's browser details, session information, and any data sent in the
    request. This parameter allows the view function
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            role = user.role  # Utilise user, pas request.user
            if role == 'ADMIN':
                return redirect('admin_dashboard')
            elif role == 'ENSEIGNANT':
                return redirect('enseignant_dashboard')
            elif role == 'ELEVE':
                return redirect('eleve_dashboard')
            elif role == 'PARENT':
                return redirect('parent_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Incorrect username or password.')
    
    return render(request, 'login.html')

def logout_view(request):
    """
    This function handles the user logout process in a Python web application.
    
    :param request: The `request` parameter in the `logout_view` function is typically an HttpRequest
    object that represents the current request made by the user to log out of the system. This object
    contains information about the request, such as the user making the request, any data sent with the
    request, and other metadata related
    """
    """Complete disconnection view"""
    if request.user.is_authenticated:
        username = request.user.get_full_name()
        logout(request)
        messages.success(request, f'Déconnexion réussie. Au revoir {username} !')
    else:
        messages.info(request, 'Vous n\'étiez pas connecté.')
    
    # Rediriger vers la page de connexion
    return redirect('login')

def teacher_subjects(request):
    """
    This function likely retrieves a list of subjects taught by a teacher based on a request.
    
    :param request: The `request` parameter in the `teacher_subjects` function likely refers to an HTTP
    request object that is being passed to this function. This object contains information about the
    incoming request, such as the request method, headers, and data. The function may use this object to
    extract any necessary information from
    """
    """View to display the teacher's subjects"""
    if request.user.role != 'ENSEIGNANT':
        messages.error(request, 'Access denied.')
        return redirect('login')
    try:
        enseignant = Enseignant.objects.get(user=request.user)
        matieres = enseignant.matieres.all()
        context = {
            'enseignant': enseignant,
            'matieres': matieres,
        }
        return render(request, 'teacher_subjects.html', context)
    except Enseignant.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('login')
from django.contrib.auth.decorators import login_required

# Vue pour les appels du jour (reconnaissance faciale)
@login_required
def teacher_attendance_today(request):
    if request.user.role != 'ENSEIGNANT':
        messages.error(request, 'Access denied.')
        return redirect('login')
    try:
        # Récupération des cours de l'enseignant pour aujourd'hui
        enseignant = Enseignant.objects.get(user=request.user)
        cours_aujourd_hui = Cours.objects.filter(
            enseignant=enseignant,
            date=timezone.now().date()
        ).order_by('heure_debut')
        
        # Récupération de la date d'aujourd'hui
        today = timezone.now().date()
        
        # Autres données pour le contexte
        total_students = User.objects.filter(role='ELEVE').count()
        total_teachers = User.objects.filter(role='ENSEIGNANT').count()
        total_parents = User.objects.filter(role='PARENT').count()
        total_admins = User.objects.filter(role='ADMIN').count()
        taux_presence = 0.0  # À calculer selon vos besoins
        active_classes = Classe.objects.count()
        absences_signalees = Presence.objects.filter(statut='ABSENT').count()
        sessions_en_cours = SessionAppel.objects.filter(statut='EN_COURS').count()
        recent_feedbacks = []  # À remplir selon vos besoins
        recent_notifications = []  # À remplir selon vos besoins
        date_limite = timezone.now().date() + timedelta(days=7)

        # Activités récentes
        recent_activities = []
        # Dernière présence
        derniere_presence = Presence.objects.order_by('-date_creation').first()
        if derniere_presence:
            recent_activities.append({
                'type': 'Présence',
                'description': f'{derniere_presence.eleve.user.get_full_name()} - {derniere_presence.get_statut_display()}',
                'time': derniere_presence.date_creation.strftime('%H:%M'),
                'icon': 'fas fa-user-check',
                'color': 'success' if derniere_presence.statut == 'PRESENT' else 'warning'
            })
        # Dernière session d'appel
        derniere_session = SessionAppel.objects.order_by('-date_debut').first()
        if derniere_session:
            recent_activities.append({
                'type': "Session d'appel",
                'description': f'Session {derniere_session.cours.matiere.nom} - {derniere_session.cours.classe.nom}',
                'time': derniere_session.date_debut.strftime('%H:%M'),
                'icon': 'fas fa-clipboard-check',
                'color': 'primary'
            })
        # Dernier utilisateur créé
        dernier_utilisateur = User.objects.order_by('-date_joined').first()
        if dernier_utilisateur:
            recent_activities.append({
                'type': 'Nouvel utilisateur',
                'description': f'{dernier_utilisateur.get_full_name()} ({dernier_utilisateur.get_role_display()})',
                'time': dernier_utilisateur.date_joined.strftime('%H:%M'),
                'icon': 'fas fa-user-plus',
                'color': 'info'
            })

        context = {
            'user': request.user,
            'enseignant': enseignant,
            'today': today,
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_parents': total_parents,
            'total_admins': total_admins,
            'attendance_rate': taux_presence,
            'active_classes': active_classes,
            'absences_signalees': absences_signalees,
            'cours_aujourd_hui': cours_aujourd_hui,
            'sessions_en_cours': sessions_en_cours,
            'recent_feedbacks': recent_feedbacks,
            'recent_notifications': recent_notifications,
            'recent_activities': recent_activities,
            'date_limite': date_limite,
        }
        return render(request, 'teacher_attendance_today.html', context)
    except Exception as e:
        # En cas d'erreur, utiliser des données par défaut
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erreur lors du chargement du tableau de bord: {str(e)}')
        context = {
            'user': request.user,
            'total_students': 0,
            'total_teachers': 0,
            'total_parents': 0,
            'total_admins': 0,
            'attendance_rate': 0.0,
            'active_classes': 0,
            'absences_signalees': 0,
            'cours_aujourd_hui': 0,
            'sessions_en_cours': 0,
            'recent_feedbacks': [],
            'recent_notifications': [],
            'recent_activities': [],
            'error': 'Erreur lors du chargement des données'
        }
        return render(request, 'teacher_attendance_today.html', context)

@login_required
def admin_users(request):
    """
    This function likely handles requests related to admin users in a Python web application.
    
    :param request: The `request` parameter in the `admin_users` function is typically an object that
    represents the HTTP request made to the server. It contains information such as the request method
    (GET, POST, etc.), headers, user data, and any data sent in the request body. This parameter allows
    the function
    """
    """User management views"""
    if not hasattr(request.user, 'role') or request.user.role.upper() != 'ADMIN':
        messages.error(request, "Accès non autorisé")
        return redirect('login')
    
    context = {
        'user': request.user,
        'users': [
            {'id': 1, 'name': 'Marie Dubois', 'email': 'marie.dubois@email.com', 'role': 'eleve', 'status': 'active', 'lastLogin': '2024-01-15 08:30'},
            {'id': 2, 'name': 'Thomas Martin', 'email': 'thomas.martin@email.com', 'role': 'enseignant', 'status': 'active', 'lastLogin': '2024-01-15 07:45'},
            {'id': 3, 'name': 'Emma Rousseau', 'email': 'emma.rousseau@email.com', 'role': 'parent', 'status': 'active', 'lastLogin': '2024-01-14 18:20'},
        ]
    }
    return render(request, 'admin_users.html', context)



@login_required
def admin_schedule(request):
    """
    This function likely handles the scheduling of administrative tasks based on the request input.
    
    :param request: The `request` parameter in the `admin_schedule` function typically refers to the
    HTTP request object that is sent to the server when a user accesses a web page. This object contains
    information about the request, such as the URL, headers, and any data sent with the request. In a
    Django view
    """
    """Time management view"""
    if not hasattr(request.user, 'role') or request.user.role.upper() != 'ADMIN':
        messages.error(request, "Accès non autorisé")
        return redirect('login')
    
    context = {
        'user': request.user,
        'schedule_data': {
            'total_courses': 156,
            'weekly_hours': '26h',
            'total_rooms': 12,
            'conflicts': 0
        }
    }
    return render(request, 'admin_schedule.html', context)

@login_required
def admin_attendance(request):
    """
    This function likely handles attendance tracking for administrative purposes.
    
    :param request: The `request` parameter in the `admin_attendance` function is typically used in web
    development with frameworks like Django. It represents an HTTP request that is sent to the server,
    and it contains information about the request made by the client, such as the URL, method (GET,
    POST, etc
    """
    """View of presences (global view)"""
    if not hasattr(request.user, 'role') or request.user.role.upper() != 'ADMIN':
        messages.error(request, "Accès non autorisé")
        return redirect('login')
    
    context = {
        'user': request.user,
        'attendance_summary': {
            'total_students': 847,
            'present_today': 798,
            'absent_today': 49,
            'late_today': 23,
            'attendance_rate': 94.2
        }
    }
    return render(request, 'admin_attendance.html', context)

@login_required
def admin_stats(request):
    """
    This function likely retrieves and displays statistics related to an admin user.
    
    :param request: The `request` parameter in the `admin_stats` function is typically an object that
    contains information about the current HTTP request, including data such as headers, user
    information, and any data sent with the request. This parameter allows the function to access and
    process information related to the request being made to the
    """
    """Statistics view"""
    if not hasattr(request.user, 'role') or request.user.role.upper() != 'ADMIN':
        messages.error(request, "Accès non autorisé")
        return redirect('login')
    
    context = {
        'user': request.user,
        'stats_data': {
            'monthly_attendance': [92, 94, 96, 95, 93, 97],
            'class_performance': [
                {'class': '6èmeA', 'attendance': 96.5, 'performance': 8.2},
                {'class': '5èmeB', 'attendance': 94.8, 'performance': 7.8},
                {'class': '4èmeC', 'attendance': 93.2, 'performance': 7.5},
            ]
        }
    }
    return render(request, 'admin_stats.html', context)

@login_required
def admin_feedback(request):
    """Vue pour gérer les feedbacks des parents"""
    if not hasattr(request.user, 'role') or request.user.role.upper() != 'ADMIN':
        messages.error(request, "Accès non autorisé")
        return redirect('login')
    
    # Récupérer tous les feedbacks avec les relations
    feedbacks = Feedback.objects.select_related(
        'parent__user', 
        'eleve__user', 
        'cours__matiere', 
        'cours__classe',
        'reponse_par'
    ).order_by('-date_creation')
    
    # Filtres
    statut_filter = request.GET.get('statut', '')
    type_filter = request.GET.get('type', '')
    priorite_filter = request.GET.get('priorite', '')
    search_query = request.GET.get('search', '')
    
    if statut_filter:
        feedbacks = feedbacks.filter(statut=statut_filter)
    if type_filter:
        feedbacks = feedbacks.filter(type_feedback=type_filter)
    if priorite_filter:
        feedbacks = feedbacks.filter(priorite=priorite_filter)
    if search_query:
        feedbacks = feedbacks.filter(
            Q(sujet__icontains=search_query) |
            Q(message__icontains=search_query) |
            Q(parent__user__first_name__icontains=search_query) |
            Q(parent__user__last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(feedbacks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    total_feedbacks = Feedback.objects.count()
    nouveaux_feedbacks = Feedback.objects.filter(statut='NOUVEAU').count()
    en_cours_feedbacks = Feedback.objects.filter(statut='EN_COURS').count()
    repondus_feedbacks = Feedback.objects.filter(statut='REPONDU').count()
    
    context = {
        'user': request.user,
        'page_obj': page_obj,
        'feedbacks': page_obj.object_list,
        'total_feedbacks': total_feedbacks,
        'nouveaux_feedbacks': nouveaux_feedbacks,
        'en_cours_feedbacks': en_cours_feedbacks,
        'repondus_feedbacks': repondus_feedbacks,
        'statut_filter': statut_filter,
        'type_filter': type_filter,
        'priorite_filter': priorite_filter,
        'search_query': search_query,
        'statut_choices': Feedback.STATUT_CHOICES,
        'type_choices': Feedback.TYPE_CHOICES,
        'priorite_choices': Feedback.PRIORITE_CHOICES,
    }
    return render(request, 'admin_feedback.html', context)

@login_required
def admin_feedback_detail(request, feedback_id):
    """Vue pour voir et répondre à un feedback spécifique"""
    if not hasattr(request.user, 'role') or request.user.role.upper() != 'ADMIN':
        messages.error(request, "Accès non autorisé")
        return redirect('login')
    
    try:
        feedback = get_object_or_404(Feedback, id=feedback_id)
    except Feedback.DoesNotExist:
        messages.error(request, "Feedback non trouvé")
        return redirect('admin_feedback')
    
    if request.method == 'POST':
        # Mettre à jour le feedback
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_statut = request.POST.get('statut')
            new_priorite = request.POST.get('priorite')
            
            feedback.statut = new_statut
            feedback.priorite = new_priorite
            feedback.save()
            
            messages.success(request, f'Statut mis à jour: {feedback.get_statut_display()}')
            
        elif action == 'respond':
            reponse = request.POST.get('reponse', '').strip()
            if reponse:
                feedback.reponse = reponse
                feedback.reponse_par = request.user
                feedback.date_reponse = timezone.now()
                feedback.statut = 'REPONDU'
                feedback.save()
                
                messages.success(request, 'Réponse envoyée avec succès')
            else:
                messages.error(request, 'Veuillez saisir une réponse')
        
        return redirect('admin_feedback_detail', feedback_id=feedback_id)
    
    context = {
        'feedback': feedback,
        'user': request.user,
        'statut_choices': Feedback.STATUT_CHOICES,
        'priorite_choices': Feedback.PRIORITE_CHOICES,
    }
    return render(request, 'admin_feedback_detail.html', context)

@login_required
def admin_notifications(request):
    """
    This function handles admin notifications for a web application.
    
    :param request: The `request` parameter in the `admin_notifications` function is typically an object
    that contains information about the current HTTP request, such as the user making the request, any
    data being sent with the request, and other relevant details. This parameter allows the function to
    access and interact with the incoming request data
    """
    """View of the notifications sent"""
    if not hasattr(request.user, 'role') or request.user.role.upper() != 'admin':
        messages.error(request, "Accès non autorisé")
        return redirect('login')
    
    context = {
        'user': request.user,
        'notifications': [
            {'id': 1, 'type': 'Absence signalée', 'recipient': 'Parent de Marie Dubois', 'class': '3èmeB', 'sent_at': '2024-01-15 08:30', 'status': 'Envoyée'},
            {'id': 2, 'type': 'Retard signalé', 'recipient': 'Parent de Thomas Martin', 'class': '4èmeA', 'sent_at': '2024-01-15 07:45', 'status': 'Envoyée'},
        ]
    }
    return render(request, 'admin_notifications.html', context)

@login_required
def admin_export(request):
    """
    This function is likely used to handle exporting data for an admin user in a web application.
    
    :param request: The `request` parameter in the `admin_export` function is typically an object that
    contains information about the current HTTP request, including data passed in the request, user
    authentication details, and other metadata related to the request. This parameter allows the
    function to access and interact with the incoming request data and process
    """
    """View of registers export"""
    if not hasattr(request.user, 'role') or request.user.role.upper() != 'ADMIN':
        messages.error(request, "Accès non autorisé")
        return redirect('login')
    
    context = {
        'user': request.user,
        'export_options': [
            {'name': 'Registre des présences', 'format': 'Excel, PDF', 'period': 'Mensuel'},
            {'name': 'Rapport des absences', 'format': 'Excel, PDF', 'period': 'Hebdomadaire'},
            {'name': 'Statistiques des classes', 'format': 'Excel, PDF', 'period': 'Trimestriel'},
        ]
    }
    return render(request, 'admin_export.html', context)

@login_required
def admin_settings(request):
    """
    This function likely handles the settings for an admin user in a web application.
    
    :param request: The `request` parameter in the `admin_settings` function is typically an object that
    contains information about the current HTTP request, such as the user making the request, the method
    used (GET, POST, etc.), and any data sent with the request. This parameter allows the function to
    access and interact
    """
    """System parameters view"""
    if not hasattr(request.user, 'role') or request.user.role.upper() != 'ADMIN':
        messages.error(request, "Accès non autorisé")
        return redirect('login')
    
    context = {
        'user': request.user,
        'system_settings': {
            'notifications_enabled': True,
            'auto_backup': True,
            'maintenance_mode': False,
            'session_timeout': 30,
        }
    }
    return render(request, 'admin_settings.html', context)

@login_required
def admin_create_user(request):
    """
    This function is likely used to create a new user account with administrative privileges.
    
    :param request: The `request` parameter in the `admin_create_user` function likely refers to an HTTP
    request object that contains information about the incoming request, such as the user's input data,
    headers, and other relevant details. This parameter allows the function to access and process the
    data sent by the user when creating
    """
    """View to create a new user"""
    if not hasattr(request.user, 'role') or request.user.role.upper() != 'ADMIN':
        messages.error(request, "Accès non autorisé")
        return JsonResponse({'success': False, 'message': 'Accès non autorisé'}, status=403)
    
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            first_name = request.POST.get('firstName')
            last_name = request.POST.get('lastName')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            role = request.POST.get('role')
            status = request.POST.get('status', 'active')
            telephone = request.POST.get('telephone', '')
            adresse = request.POST.get('adresse', '')
            
            # Validation des champs obligatoires
            if not all([first_name, last_name, email, username, password, role]):
                return JsonResponse({
                    'success': False, 
                    'message': 'Tous les champs obligatoires doivent être remplis'
                }, status=400)
            
            # Vérifier que l'utilisateur n'existe pas déjà
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False, 
                    'message': 'Ce nom d\'utilisateur existe déjà'
                }, status=400)
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False, 
                    'message': 'Cet email est déjà utilisé'
                }, status=400)
            
            # Créer l'utilisateur de base
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                telephone=telephone,
                adresse=adresse
            )
            
            # Créer les modèles spécifiques selon le rôle
            if role == 'ELEVE':
                classe_id = request.POST.get('classe')
                date_naissance = request.POST.get('dateNaissance')
                
                # Vérifier que la classe est fournie pour les élèves
                if not classe_id:
                    # Supprimer l'utilisateur créé car la classe est obligatoire
                    user.delete()
                    return JsonResponse({
                        'success': False, 
                        'message': 'La classe est obligatoire pour un élève'
                    }, status=400)
                
                # Assigner la date de naissance à l'utilisateur si fournie
                if date_naissance:
                    user.date_naissance = date_naissance
                    user.save()
                
                try:
                    classe = Classe.objects.get(nom=classe_id)
                    eleve = Eleve.objects.create(
                        user=user,
                        classe=classe
                    )
                    
                    # Gérer la photo de référence si fournie
                    if 'photoReference' in request.FILES:
                        eleve.photo_reference = request.FILES['photoReference']
                        eleve.save()
                        
                except Classe.DoesNotExist:
                    # Supprimer l'utilisateur créé car la classe n'existe pas
                    user.delete()
                    return JsonResponse({
                        'success': False, 
                        'message': f'La classe {classe_id} n\'existe pas'
                    }, status=400)
            
            elif role == 'ENSEIGNANT':
                specialite = request.POST.get('specialite', '')
                date_embauche = request.POST.get('dateEmbauche')
                
                # Utiliser la date d'aujourd'hui si aucune date d'embauche n'est fournie
                if not date_embauche:
                    date_embauche = timezone.now().date()
                
                enseignant = Enseignant.objects.create(
                    user=user,
                    specialite=specialite,
                    date_embauche=date_embauche
                )
                
                # Assigner les matières si fournies
                matieres = request.POST.getlist('matieres')
                if matieres:
                    for matiere_code in matieres:
                        try:
                            matiere = Matiere.objects.get(code=matiere_code)
                            enseignant.matieres.add(matiere)
                        except Matiere.DoesNotExist:
                            pass
                
                # Assigner les classes si fournies
                classes = request.POST.getlist('classes')
                if classes:
                    for classe_nom in classes:
                        try:
                            classe = Classe.objects.get(nom=classe_nom)
                            enseignant.classes.add(classe)
                        except Classe.DoesNotExist:
                            pass
            
            elif role == 'PARENT':
                parent = Parent.objects.create(
                    user=user
                )
                
                # Lier les enfants si leurs emails sont fournis
                enfants_emails = request.POST.get('enfants', '')
                if enfants_emails:
                    for email in enfants_emails.split(','):
                        email = email.strip()
                        if email:
                            try:
                                enfant_user = User.objects.get(email=email, role='ELEVE')
                                enfant = Eleve.objects.get(user=enfant_user)
                                enfant.parent = parent
                                enfant.save()
                            except (User.DoesNotExist, Eleve.DoesNotExist):
                                pass
            
            # Définir le statut de l'utilisateur
            if status == 'inactive':
                user.is_active = False
                user.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Utilisateur {first_name} {last_name} créé avec succès',
                'user_id': user.id
            })
            
        except Exception as e:
            # En cas d'erreur, supprimer l'utilisateur créé pour éviter les orphelins
            if 'user' in locals():
                try:
                    user.delete()
                except:
                    pass
            
            # Log de l'erreur pour le débogage
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Erreur lors de la création d\'utilisateur: {str(e)}')
            
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de la création: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)

@login_required
def admin_get_users(request):
    """
    This function is likely designed to retrieve user information for administrative purposes.
    
    :param request: The `admin_get_users` function likely takes a `request` parameter, which is commonly
    used in web development frameworks like Django or Flask to represent an HTTP request made to the
    server. This parameter allows the function to access information about the request, such as headers,
    data, and user authentication details
    """
    """API view to recover users with pagination"""
    if not hasattr(request.user, 'role') or request.user.role.upper() != 'ADMIN':
        return JsonResponse({'success': False, 'message': 'Accès non autorisé'}, status=403)
    
    try:
        # Paramètres de pagination
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        # Filtres
        role_filter = request.GET.get('role', '')
        status_filter = request.GET.get('status', '')
        search_query = request.GET.get('search', '')
        
        # Query de base
        users = User.objects.all().order_by('-date_joined')
        
        # Appliquer les filtres
        if role_filter:
            users = users.filter(role__iexact=role_filter)
        
        if status_filter:
            if status_filter == 'active':
                users = users.filter(is_active=True)
            elif status_filter == 'inactive':
                users = users.filter(is_active=False)
            elif status_filter == 'suspended':
                users = users.filter(is_active=False)  # Pour l'instant, on considère les inactifs comme suspendus
        
        if search_query:
            users = users.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(users, per_page)
        page_obj = paginator.get_page(page)
        
        # Préparer les données des utilisateurs
        users_data = []
        for user in page_obj:
            user_data = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': user.role,
                'status': 'active' if user.is_active else 'inactive',
                'date_joined': user.date_joined.strftime('%d/%m/%Y %H:%M'),
                'last_login': user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'Jamais'
            }
            
            # Ajouter les informations spécifiques au rôle
            if user.role == 'ELEVE':
                try:
                    eleve = Eleve.objects.get(user=user)
                    user_data['classe'] = eleve.classe.nom if eleve.classe else 'Non assigné'
                    user_data['matricule'] = eleve.matricule
                    # Ajouter la photo de référence
                    if eleve.photo_reference:
                        user_data['photo_reference'] = eleve.photo_reference.url
                    else:
                        user_data['photo_reference'] = None
                except Eleve.DoesNotExist:
                    user_data['classe'] = 'Non assigné'
                    user_data['matricule'] = 'N/A'
                    user_data['photo_reference'] = None
            
            elif user.role == 'ENSEIGNANT':
                try:
                    enseignant = Enseignant.objects.get(user=user)
                    user_data['specialite'] = enseignant.specialite or 'Non spécifiée'
                    user_data['date_embauche'] = enseignant.date_embauche.strftime('%d/%m/%Y') if enseignant.date_embauche else 'Non spécifiée'
                except Enseignant.DoesNotExist:
                    user_data['specialite'] = 'Non spécifiée'
                    user_data['date_embauche'] = 'Non spécifiée'
            
            elif user.role == 'PARENT':
                try:
                    parent = Parent.objects.get(user=user)
                    user_data['profession'] = parent.profession or 'Non spécifiée'
                except Parent.DoesNotExist:
                    user_data['profession'] = 'Non spécifiée'
            
            users_data.append(user_data)
        
        # Statistiques
        total_users = User.objects.count()
        total_students = User.objects.filter(role='ELEVE').count()
        total_teachers = User.objects.filter(role='ENSEIGNANT').count()
        total_parents = User.objects.filter(role='PARENT').count()
        total_admins = User.objects.filter(role='ADMIN').count()
        
        return JsonResponse({
            'success': True,
            'users': users_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            },
            'stats': {
                'total_users': total_users,
                'total_students': total_students,
                'total_teachers': total_teachers,
                'total_parents': total_parents,
                'total_admins': total_admins,
            }
        })
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erreur lors de la récupération des utilisateurs: {str(e)}')
        
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la récupération des utilisateurs: {str(e)}'
        }, status=500)

@login_required
def admin_toggle_user_status(request, user_id):
    """
    This function toggles the status of a user in an admin interface.
    
    :param request: The `request` parameter typically refers to the HTTP request object that is sent to
    the server. It contains information about the request made by the client, such as headers,
    parameters, and the user making the request
    :param user_id: The `user_id` parameter in the `admin_toggle_user_status` function likely refers to
    the unique identifier of the user whose status is being toggled. This parameter is used to identify
    the specific user for whom the status is being changed, such as activating or deactivating their
    account, based on
    """
    """View to activate/deactivate a user"""
    if not hasattr(request.user, 'role') or request.user.role.upper() != 'ADMIN':
        return JsonResponse({'success': False, 'message': 'Accès non autorisé'}, status=403)
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            user.is_active = not user.is_active
            user.save()
            
            status_text = 'activé' if user.is_active else 'désactivé'
            return JsonResponse({
                'success': True,
                'message': f'Utilisateur {user.get_full_name()} {status_text} avec succès',
                'new_status': 'active' if user.is_active else 'inactive'
            })
            
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Utilisateur non trouvé'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)

@login_required
def admin_delete_user(request, user_id):
    """
    This function is used to handle a request to delete a user with a specific user ID.
    
    :param request: The `request` parameter in the `admin_delete_user` function likely refers to the
    HTTP request object that is sent to the server when a user wants to delete a specific user account.
    This object contains information about the request being made, such as the user making the request,
    the method used (e
    :param user_id: The `user_id` parameter in the `admin_delete_user` function likely refers to the
    unique identifier of the user that the admin wants to delete from the system. This parameter helps
    the function identify which user record to delete from the database or perform any other necessary
    actions related to deleting a user account
    """
    """View to delete a user"""
    if not hasattr(request.user, 'role') or request.user.role.upper() != 'ADMIN':
        return JsonResponse({'success': False, 'message': 'Accès non autorisé'}, status=403)
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            
            # Empêcher la suppression de l'utilisateur connecté
            if user == request.user:
                return JsonResponse({'success': False, 'message': 'Vous ne pouvez pas supprimer votre propre compte'}, status=400)
            
            user_name = user.get_full_name()
            user.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Utilisateur {user_name} supprimé avec succès'
            })
            
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Utilisateur non trouvé'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)

@login_required
def admin_get_user_details(request, user_id):
    """
    This function is used to retrieve details of a specific user identified by their user ID in an admin
    context.
    
    :param request: The `request` parameter in the `admin_get_user_details` function likely refers to an
    HTTP request object that contains information about the incoming request such as headers,
    parameters, and body data. This parameter is commonly used in web development frameworks like Django
    or Flask to handle incoming requests and provide appropriate responses
    :param user_id: The `admin_get_user_details` function takes two parameters:
    """
    """View to recover the details of a user for modification"""
    if not hasattr(request.user, 'role') or request.user.role.upper() != 'ADMIN':
        return JsonResponse({'success': False, 'message': 'Accès non autorisé'}, status=403)
    
    try:
        user = User.objects.get(id=user_id)
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role,
            'status': 'active' if user.is_active else 'inactive',
            'telephone': user.telephone or '',
            'adresse': user.adresse or '',
        }
        
        # Ajouter les informations spécifiques au rôle
        if user.role == 'ELEVE':
            try:
                eleve = Eleve.objects.get(user=user)
                user_data['classe'] = eleve.classe.nom if eleve.classe else ''
                user_data['date_naissance'] = user.date_naissance.strftime('%Y-%m-%d') if user.date_naissance else ''
            except Eleve.DoesNotExist:
                user_data['classe'] = ''
                user_data['date_naissance'] = ''
        
        elif user.role == 'ENSEIGNANT':
            try:
                enseignant = Enseignant.objects.get(user=user)
                user_data['specialite'] = enseignant.specialite or ''
                user_data['date_embauche'] = enseignant.date_embauche.strftime('%Y-%m-%d') if enseignant.date_embauche else ''
            except Enseignant.DoesNotExist:
                user_data['specialite'] = ''
                user_data['date_embauche'] = ''
        
        elif user.role == 'PARENT':
            try:
                parent = Parent.objects.get(user=user)
                user_data['profession'] = parent.profession or ''
                user_data['lieu_travail'] = parent.lieu_travail or ''
            except Parent.DoesNotExist:
                user_data['profession'] = ''
                user_data['lieu_travail'] = ''
        
        return JsonResponse({
            'success': True,
            'user': user_data
        })
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Utilisateur non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'}, status=500)

@login_required
def admin_update_user(request, user_id):
    """
    This function is used to update user information for an admin user in a web application.
    
    :param request: The `request` parameter in the `admin_update_user` function likely refers to an HTTP
    request object that contains information about the current request being made to the server. This
    object typically includes details such as headers, parameters, and the body of the request. It
    allows the function to access and process data
    :param user_id: The `user_id` parameter in the `admin_update_user` function likely refers to the
    unique identifier of the user whose information is being updated. This parameter helps the function
    identify which user's data needs to be modified or updated
    """
    """View to modify a user"""
    if not hasattr(request.user, 'role') or request.user.role.upper() != 'ADMIN':
        return JsonResponse({'success': False, 'message': 'Accès non autorisé'}, status=403)
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            
            # Mettre à jour les informations de base
            user.first_name = request.POST.get('firstName', user.first_name)
            user.last_name = request.POST.get('lastName', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.telephone = request.POST.get('telephone', user.telephone)
            user.adresse = request.POST.get('adresse', user.adresse)
            
            # Mettre à jour le statut
            status = request.POST.get('status', 'active')
            user.is_active = (status == 'active')
            
            # Mettre à jour la date de naissance si fournie
            date_naissance = request.POST.get('dateNaissance')
            if date_naissance:
                user.date_naissance = date_naissance
            
            user.save()
            
            # Mettre à jour les informations spécifiques au rôle
            if user.role == 'ELEVE':
                try:
                    eleve = Eleve.objects.get(user=user)
                    classe_id = request.POST.get('classe')
                    if classe_id:
                        classe = Classe.objects.get(nom=classe_id)
                        eleve.classe = classe
                        eleve.save()
                except (Eleve.DoesNotExist, Classe.DoesNotExist):
                    pass
            
            elif user.role == 'ENSEIGNANT':
                try:
                    enseignant = Enseignant.objects.get(user=user)
                    enseignant.specialite = request.POST.get('specialite', '')
                    date_embauche = request.POST.get('dateEmbauche')
                    if date_embauche:
                        enseignant.date_embauche = date_embauche
                    enseignant.save()
                except Enseignant.DoesNotExist:
                    pass
            
            elif user.role == 'PARENT':
                try:
                    parent = Parent.objects.get(user=user)
                    parent.profession = request.POST.get('profession', '')
                    parent.lieu_travail = request.POST.get('lieu_travail', '')
                    parent.save()
                except Parent.DoesNotExist:
                    pass
            
            return JsonResponse({
                'success': True,
                'message': f'Utilisateur {user.get_full_name()} modifié avec succès'
            })
            
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Utilisateur non trouvé'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)

@login_required
def enseignant_dashboard(request):
    """
    This function likely serves as a view for an "enseignant" (teacher) dashboard in a web application.
    
    :param request: The `request` parameter in the `enseignant_dashboard` function is typically an
    HttpRequest object that represents the current request from the user. It contains information about
    the request, such as the user's session, GET and POST data, and other metadata related to the
    request. This parameter allows you to access
    """
    if request.user.role != 'ENSEIGNANT':
        return redirect('login')
    
    try:
        enseignant = Enseignant.objects.get(user=request.user)
        
        # Cours du jour (exclure ceux dont l'appel est terminé)
        aujourd_hui = timezone.now().date()
        cours_aujourd_hui = Cours.objects.filter(
            enseignant=enseignant,
            date=aujourd_hui
        ).exclude(
            sessionappel__statut='TERMINE'
        ).order_by('heure_debut')
        
        # Ajouter les informations sur les sessions d'appel pour chaque cours
        cours_with_sessions = []
        for cours in cours_aujourd_hui:
            session_appel = SessionAppel.objects.filter(cours=cours).first()
            cours_with_sessions.append({
                'cours': cours,
                'session_appel': session_appel,
                'appel_status': session_appel.statut if session_appel else 'PAS_DEMARRE'
            })
        
        # Sessions d'appel en cours
        sessions_en_cours = SessionAppel.objects.filter(
            enseignant=enseignant,
            statut='EN_COURS'
        )
        
        # Calculer le nombre d'élèves absents aujourd'hui
        nb_eleves_absents = 0
        if sessions_en_cours.exists():
            for session in sessions_en_cours:
                absents = Presence.objects.filter(
                    session_appel=session,
                    statut='ABSENT'
                ).count()
                nb_eleves_absents += absents
        
        # Calculer le taux de présence de la semaine
        debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        fin_semaine = debut_semaine + timedelta(days=6)
        
        presences_semaine = Presence.objects.filter(
            session_appel__enseignant=enseignant,
            session_appel__cours__date__gte=debut_semaine,
            session_appel__cours__date__lte=fin_semaine
        )
        
        total_presences = presences_semaine.count()
        presences_validees = presences_semaine.filter(statut__in=['PRESENT', 'RETARD']).count()
        
        taux_presence = round((presences_validees / total_presences * 100) if total_presences > 0 else 0, 1)
        
        # Nombre de classes actives (classes où l'enseignant a des cours)
        classes_actives = Classe.objects.filter(
            cours__enseignant=enseignant
        ).distinct()
        nb_classes_actives = classes_actives.count()
        
        context = {
            'enseignant': enseignant,
            'cours_aujourd_hui': cours_aujourd_hui,
            'cours_with_sessions': cours_with_sessions,
            'sessions_en_cours': sessions_en_cours,
            'nb_eleves_absents': nb_eleves_absents,
            'taux_presence': taux_presence,
            'nb_classes_actives': nb_classes_actives,
        }
        
        return render(request, 'dashboard_teacher.html', context)
        
    except Enseignant.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('login')

@login_required
def eleve_dashboard(request):
    """
    This function likely serves as a view for an "eleve" dashboard in a Python web application.
    
    :param request: The `request` parameter in the `eleve_dashboard` function is typically used in
    Django web development to represent an HTTP request from a client. It contains information about the
    request, such as the user making the request, any data sent with the request, and other metadata
    related to the request. This
    """
    if request.user.role != 'ELEVE':
        return redirect('login')
    
    try:
        eleve = Eleve.objects.get(user=request.user)
        
        # Présences du mois
        debut_mois = timezone.now().replace(day=1)
        presences_mois = Presence.objects.filter(
            eleve=eleve,
            session_appel__cours__date__gte=debut_mois
        ).order_by('-session_appel__cours__date')
        
        # Cours du jour
        aujourd_hui = timezone.now().date()
        cours_aujourd_hui = Cours.objects.filter(
            classe=eleve.classe,
            date=aujourd_hui
        ).order_by('heure_debut')
        
        context = {
            'eleve': eleve,
            'presences_mois': presences_mois,
            'cours_aujourd_hui': cours_aujourd_hui,
        }
        
        return render(request, 'dashboard_eleve.html', context)
        
    except Eleve.DoesNotExist:
        messages.error(request, 'Profil élève non trouvé.')
        return redirect('login')

@login_required
def parent_dashboard(request):
    """
    This function likely serves as a view for a parent dashboard in a web application.
    
    :param request: The `request` parameter in the `parent_dashboard` function is typically an object
    that contains information about the current HTTP request. It includes details such as the user
    making the request, any data being sent with the request, and other metadata related to the request.
    This parameter allows the function to access and
    """
    if request.user.role != 'PARENT':
        return redirect('login')
    
    try:
        parent = Parent.objects.get(user=request.user)
        
        # Enfants du parent
        enfants = Eleve.objects.filter(parent=parent).select_related('classe', 'user')
        
        # Récupérer le premier enfant pour l'affichage principal (ou le seul enfant)
        premier_enfant = enfants.first() if enfants.exists() else None
        
        # Présences des enfants du mois
        debut_mois = timezone.now().replace(day=1)
        presences_enfants = Presence.objects.filter(
            eleve__in=enfants,
            session_appel__cours__date__gte=debut_mois
        ).order_by('-session_appel__cours__date')
        
        # Calculer les statistiques pour le premier enfant
        stats_enfant = {}
        if premier_enfant:
            # Absences du mois
            absences_mois = presences_enfants.filter(
                eleve=premier_enfant,
                statut='ABSENT'
            ).count()
            
            # Retards du mois
            retards_mois = presences_enfants.filter(
                eleve=premier_enfant,
                statut='RETARD'
            ).count()
            
            # Taux de présence
            total_cours_mois = presences_enfants.filter(eleve=premier_enfant).count()
            presences_mois = presences_enfants.filter(
                eleve=premier_enfant,
                statut='PRESENT'
            ).count()
            
            taux_presence = (presences_mois / total_cours_mois * 100) if total_cours_mois > 0 else 0
            
            stats_enfant = {
                'absences': absences_mois,
                'retards': retards_mois,
                'taux_presence': round(taux_presence, 1),
                'total_cours': total_cours_mois
            }
        
        context = {
            'parent': parent,
            'enfants': enfants,
            'premier_enfant': premier_enfant,
            'presences_enfants': presences_enfants,
            'stats_enfant': stats_enfant,
            'current_month': timezone.now().strftime('%B %Y'),
        }
        
        return render(request, 'dashboard_parent.html', context)
        
    except Parent.DoesNotExist:
        messages.error(request, 'Profil parent non trouvé.')
        return redirect('login')

@login_required
def qr_code_scan(request, cours_id):
    """
    This Python function is likely designed to handle a QR code scan request for a specific course ID.
    
    :param request: The `request` parameter in the `qr_code_scan` function likely refers to an HTTP
    request object in a web application framework such as Django or Flask. This object contains
    information about the incoming request made to the server, including data sent by the client,
    headers, and other relevant details
    :param cours_id: The `qr_code_scan` function seems to be a view or endpoint in a Django web
    application that handles scanning QR codes. The `request` parameter is the HTTP request object sent
    to the view, containing information about the request made by the client. The `cours_id` parameter
    appears to be
    """
    """View for the QR code scan of a specific course"""
    if request.user.role != 'ENSEIGNANT':
        return redirect('login')
    
    try:
        enseignant = Enseignant.objects.get(user=request.user)
        cours = get_object_or_404(Cours, id=cours_id, enseignant=enseignant)
        
        # Vérifier que le cours est aujourd'hui
        if cours.date != timezone.now().date():
            messages.error(request, 'Ce cours n\'est pas prévu aujourd\'hui.')
            return redirect('enseignant_dashboard')
        
        # Récupérer les élèves de la classe
        eleves = Eleve.objects.filter(classe=cours.classe).order_by('user__last_name', 'user__first_name')
        
        # Vérifier s'il y a déjà une session d'appel
        session_appel, created = SessionAppel.objects.get_or_create(
            cours=cours,
            enseignant=enseignant,
            statut='EN_COURS',
            defaults={'methode': 'QR_CODE'}
        )
        
        # Créer les enregistrements de présence s'ils n'existent pas
        for eleve in eleves:
            Presence.objects.get_or_create(
                session_appel=session_appel,
                eleve=eleve,
                defaults={
                    'statut': 'ABSENT',
                    'methode_detection': 'QR_CODE'
                }
            )
        
        context = {
            'cours': cours,
            'eleves': eleves,
            'session_appel': session_appel,
        }
        
        return render(request, 'qr_code_scan_enhanced.html', context)
        
    except Enseignant.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Erreur: {str(e)}')
        return redirect('enseignant_dashboard')

@login_required
def scan_qr_eleves(request, cours_id):
    """
    This function is likely designed to scan QR codes for student attendance in a specific course.
    
    :param request: The `request` parameter in the `scan_qr_eleves` function likely refers to an HTTP
    request object in a web application framework such as Django or Flask. This object contains
    information about the current request being made to the server, including data sent by the client,
    headers, and other metadata
    :param cours_id: The `scan_qr_eleves` function seems to be a part of a Django view in a web
    application. The `request` parameter is the HTTP request object that Django passes to the view,
    containing information about the incoming request. The `cours_id` parameter is likely the identifier
    of the
    """
    """View for the QR scan Codes of students with smartphone"""
    if request.user.role != 'ENSEIGNANT':
        return redirect('login')
    
    try:
        enseignant = Enseignant.objects.get(user=request.user)
        cours = get_object_or_404(Cours, id=cours_id, enseignant=enseignant)
        
        # Vérifier que le cours est aujourd'hui
        if cours.date != timezone.now().date():
            messages.error(request, 'Ce cours n\'est pas prévu aujourd\'hui.')
            return redirect('enseignant_dashboard')
        
        # Récupérer les élèves de la classe
        eleves = Eleve.objects.filter(classe=cours.classe).order_by('user__last_name', 'user__first_name')
        
        # Créer ou récupérer la session d'appel
        session_appel, created = SessionAppel.objects.get_or_create(
            cours=cours,
            enseignant=enseignant,
            statut='EN_COURS',
            defaults={'methode': 'QR_CODE_SMARTPHONE'}
        )
        
        # Créer les enregistrements de présence s'ils n'existent pas
        for eleve in eleves:
            Presence.objects.get_or_create(
                session_appel=session_appel,
                eleve=eleve,
                defaults={
                    'statut': 'ABSENT',
                    'methode_detection': 'QR_CODE_SMARTPHONE'
                }
            )
        
        # Récupérer les présences actuelles
        presences = Presence.objects.filter(session_appel=session_appel)
        
        # Préparer les données des élèves avec leurs présences
        eleves_with_presence = []
        for eleve in eleves:
            presence = presences.filter(eleve=eleve).first()
            eleves_with_presence.append({
                'eleve': eleve,
                'presence': presence
            })
        
        context = {
            'cours': cours,
            'eleves_with_presence': eleves_with_presence,
            'session_appel': session_appel,
        }
        
        return render(request, 'scan_qr_eleves.html', context)
        
    except Enseignant.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'Erreur: {str(e)}')
        return redirect('enseignant_dashboard')

@login_required
def api_update_presence(request):
    """
    This function is likely used to update the presence status of a user in an API.
    
    :param request: The `request` parameter in the `api_update_presence` function likely refers to the
    HTTP request object that contains information about the incoming request, such as headers,
    parameters, and data. This parameter allows the function to access and process the data sent by the
    client making the request
    """
    """API to update the presence status of a student"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    if request.user.role != 'ENSEIGNANT':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    try:
        data = json.loads(request.body)
        presence_id = data.get('presence_id')
        nouveau_statut = data.get('statut')
        commentaire = data.get('commentaire', '')
        
        presence = get_object_or_404(Presence, id=presence_id)
        
        # Vérifier que l'enseignant est bien celui du cours
        if presence.session_appel.enseignant.user != request.user:
            return JsonResponse({'error': 'Accès non autorisé'}, status=403)
        
        # Mettre à jour le statut
        presence.statut = nouveau_statut
        if nouveau_statut in ['PRESENT', 'RETARD']:
            presence.heure_arrivee = timezone.now().time()
        else:
            presence.heure_arrivee = None
        
        presence.commentaire = commentaire
        presence.save()
        
        # Créer une notification pour le parent si absent ou en retard
        if nouveau_statut in ['ABSENT', 'RETARD'] and presence.eleve.parent:
            Notification.objects.create(
                destinataire=presence.eleve.parent.user,
                type_notification='ABSENCE' if nouveau_statut == 'ABSENT' else 'RETARD',
                titre=f"{nouveau_statut.title()} - {presence.eleve.user.get_full_name()}",
                message=f"Votre enfant {presence.eleve.user.get_full_name()} est {nouveau_statut.lower()} au cours de {presence.session_appel.cours.matiere.nom} le {presence.session_appel.cours.date.strftime('%d/%m/%Y')}.",
                lien=f"/parent/dashboard"
            )
        
        return JsonResponse({
            'success': True,
            'message': f'Statut mis à jour: {presence.get_statut_display()}',
            'presence': {
                'id': presence.id,
                'statut': presence.statut,
                'heure_arrivee': presence.heure_arrivee.isoformat() if presence.heure_arrivee else None,
                'commentaire': presence.commentaire
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Données JSON invalides'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_update_presence_from_scan(request):
    """
    This function updates the presence status based on a scan request from an API.
    
    :param request: The `request` parameter in the `api_update_presence_from_scan` function likely
    refers to the HTTP request object that contains information sent by the client to the server. This
    object typically includes data such as headers, parameters, and the request method (GET, POST, PUT,
    DELETE, etc.). You
    """
    """API to update presence status from the scan interface"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    if request.user.role != 'ENSEIGNANT':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    try:
        data = json.loads(request.body)
        eleve_id = data.get('eleve_id')
        session_id = data.get('session_id')
        nouveau_statut = data.get('statut')
        
        if not all([eleve_id, session_id, nouveau_statut]):
            return JsonResponse({'error': 'Paramètres manquants'}, status=400)
        
        # Récupérer ou créer la présence
        presence, created = Presence.objects.get_or_create(
            eleve_id=eleve_id,
            session_appel_id=session_id,
            defaults={
                'statut': nouveau_statut,
                'heure_arrivee': timezone.now().time() if nouveau_statut in ['PRESENT', 'RETARD'] else None,
                'methode_detection': 'MANUEL'
            }
        )
        
        if not created:
            # Mettre à jour le statut existant
            presence.statut = nouveau_statut
            if nouveau_statut in ['PRESENT', 'RETARD']:
                presence.heure_arrivee = timezone.now().time()
            else:
                presence.heure_arrivee = None
            presence.save()
        
        # Envoyer un email au parent selon le statut
        from .email_service import ParentNotificationService
        
        if nouveau_statut == 'PRESENT':
            # Envoyer un email de confirmation de présence
            ParentNotificationService.send_presence_confirmation_email(presence.id)
        elif nouveau_statut == 'RETARD':
            # Envoyer un email de notification de retard
            ParentNotificationService.send_retard_notification_email(presence.id)
        elif nouveau_statut == 'ABSENT':
            # Envoyer un email de notification d'absence
            ParentNotificationService.send_absence_notification_email(presence.id)
        
        # Créer une notification pour le parent si absent ou en retard
        if nouveau_statut in ['ABSENT', 'RETARD'] and presence.eleve.parent:
            Notification.objects.create(
                destinataire=presence.eleve.parent.user,
                type_notification='ABSENCE' if nouveau_statut == 'ABSENT' else 'RETARD',
                titre=f"{nouveau_statut.title()} - {presence.eleve.user.get_full_name()}",
                message=f"Votre enfant {presence.eleve.user.get_full_name()} est {nouveau_statut.lower()} au cours de {presence.session_appel.cours.matiere.nom} le {presence.session_appel.cours.date.strftime('%d/%m/%Y')}.",
                lien=f"/parent/dashboard"
            )
        
        return JsonResponse({
            'success': True,
            'message': f'Statut mis à jour: {presence.get_statut_display()}',
            'presence': {
                'id': presence.id,
                'statut': presence.statut,
                'heure_arrivee': presence.heure_arrivee.isoformat() if presence.heure_arrivee else None,
                'methode_detection': presence.methode_detection
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Données JSON invalides'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_validate_session(request):
    """
    This function is likely used to validate a session in an API request.
    
    :param request: The `request` parameter in the `api_validate_session` function likely refers to the
    HTTP request object that is received by the API endpoint. This object contains information about the
    incoming request, such as headers, parameters, and body content. The function is expected to use
    this `request` object to validate
    """
    """API to validate a call session"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    if request.user.role != 'ENSEIGNANT':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        session_appel = get_object_or_404(SessionAppel, id=session_id)
        
        # Vérifier que l'enseignant est bien celui de la session
        if session_appel.enseignant.user != request.user:
            return JsonResponse({'error': 'Accès non autorisé'}, status=403)
        
        # Finaliser la session
        session_appel.statut = 'TERMINE'
        session_appel.date_fin = timezone.now()
        session_appel.save()
        
        # Créer l'historique des présences
        presences = Presence.objects.filter(session_appel=session_appel)
        for presence in presences:
            HistoriquePresence.objects.create(
                eleve=presence.eleve,
                cours=presence.session_appel.cours,
                statut=presence.statut,
                date=presence.session_appel.cours.date,
                heure_arrivee=presence.heure_arrivee,
                methode_detection=presence.methode_detection,
                commentaire=presence.commentaire
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Session d\'appel validée avec succès',
            'session': {
                'id': str(session_appel.id),
                'statut': session_appel.statut,
                'date_fin': session_appel.date_fin.isoformat() if session_appel.date_fin else None
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Données JSON invalides'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_qr_code_scan(request):
    """
    This function is likely used to handle scanning QR codes in an API request.
    
    :param request: The `request` parameter in the `api_qr_code_scan` function likely refers to the HTTP
    request object that is sent to the server when the function is called. This object contains
    information about the request being made, such as headers, parameters, and the request method. The
    function likely uses this
    """
    """API for the QR code scan in real time"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    if request.user.role != 'ENSEIGNANT':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        qr_code_data = data.get('qr_code_data')
        
        # Récupérer la session d'appel et les élèves concernés
        session_appel = get_object_or_404(SessionAppel, id=session_id)
        
        # Vérifier que l'enseignant est bien celui du cours
        if session_appel.enseignant.user != request.user:
            return JsonResponse({'error': 'Accès non autorisé'}, status=403)
        
        # Rechercher l'élève par son matricule (contenu du QR code)
        try:
            eleve = Eleve.objects.get(matricule=qr_code_data)
            
            # Vérifier que l'élève appartient à la classe du cours
            if eleve.classe != session_appel.cours.classe:
                return JsonResponse({
                    'error': 'Cet élève n\'appartient pas à cette classe',
                    'status': 'error'
                }, status=400)
            
            # Récupérer ou créer l'enregistrement de présence
            presence, created = Presence.objects.get_or_create(
                            session_appel=session_appel,
                eleve=eleve,
                defaults={
                    'statut': 'PRESENT',
                    'methode_detection': 'QR_CODE',
                    'heure_arrivee': timezone.now().time(),
                    'niveau_confiance': 1.0  # QR code = 100% de confiance
                }
            )
            
            # Si la présence existe déjà, mettre à jour le statut
            if not created:
                if presence.statut == 'ABSENT':
                    presence.statut = 'PRESENT'
                    presence.heure_arrivee = timezone.now().time()
                    presence.methode_detection = 'QR_CODE'
                    presence.niveau_confiance = 1.0
                    presence.save()
                else:
                    return JsonResponse({
                        'message': f'{eleve.user.get_full_name()} est déjà marqué comme présent',
                        'status': 'already_present',
                        'eleve_name': eleve.user.get_full_name()
                    })
            
            # Créer une notification pour le parent
            if eleve.parent:
                Notification.objects.create(
                    destinataire=eleve.parent.user,
                    type_notification='PRESENCE',
                    titre=f"Présence confirmée - {eleve.user.get_full_name()}",
                    message=f"Votre enfant {eleve.user.get_full_name()} a été marqué présent au cours de {session_appel.cours.matiere.nom} le {session_appel.cours.date.strftime('%d/%m/%Y')}",
                    lien=f"/parent/dashboard"
                )
            
            return JsonResponse({
                'success': True,
                'message': f'Présence confirmée pour {eleve.user.get_full_name()}',
                'eleve': {
                    'id': eleve.id,
                    'name': f"{eleve.user.first_name} {eleve.user.last_name}",
                    'matricule': eleve.matricule,
                    'status': 'present',
                    'confidence': 1.0
                }
            })
            
        except Eleve.DoesNotExist:
            return JsonResponse({
                'error': 'QR code non reconnu - Élève non trouvé',
                'status': 'error'
            }, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Données JSON invalides'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_mobile_qr_scan(request):
    """
    This function is likely designed to handle API requests related to scanning QR codes with a mobile
    device.
    
    :param request: The `api_mobile_qr_scan` function appears to be a Python function that likely
    handles a request related to scanning QR codes on a mobile device. The `request` parameter is
    typically used to represent the HTTP request object that contains information sent by the client to
    the server. This object usually includes data
    """
    """API for the QR code scan from the mobile phone"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    if request.user.role != 'ENSEIGNANT':
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    try:
        data = json.loads(request.body)
        matricule = data.get('matricule')
        session_id = data.get('session_id')
        
        if not matricule or not session_id:
            return JsonResponse({'error': 'Matricule et session_id requis'}, status=400)
        
        # Récupérer la session d'appel
        session_appel = get_object_or_404(SessionAppel, id=session_id, enseignant__user=request.user)
        
        # Récupérer l'élève par matricule
        eleve = get_object_or_404(Eleve, matricule=matricule, classe=session_appel.cours.classe)
        
        # Récupérer ou créer la présence
        presence, created = Presence.objects.get_or_create(
            session_appel=session_appel,
            eleve=eleve,
            defaults={
                'statut': 'PRESENT',
                'methode_detection': 'QR_CODE',
                'heure_arrivee': timezone.now().time()
            }
        )
        
        # Si la présence existe déjà, mettre à jour le statut
        if not created:
            presence.statut = 'PRESENT'
            presence.heure_arrivee = timezone.now().time()
            presence.methode_detection = 'QR_CODE'
            presence.save()
        
        # Créer une notification de succès
        return JsonResponse({
            'success': True,
            'message': f'Présence confirmée pour {eleve.user.get_full_name()}',
            'eleve': {
                'id': eleve.id,
                'nom': eleve.user.get_full_name(),
                'matricule': eleve.matricule,
                'photo': eleve.photo_reference.url if eleve.photo_reference else None
            },
            'presence': {
                'id': presence.id,
                'statut': presence.statut,
                'heure_arrivee': presence.heure_arrivee.isoformat() if presence.heure_arrivee else None
            }
        })
        
    except Eleve.DoesNotExist:
        return JsonResponse({'error': 'Élève non trouvé'}, status=404)
    except SessionAppel.DoesNotExist:
        return JsonResponse({'error': 'Session d\'appel non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Erreur: {str(e)}'}, status=500)

@login_required
def liste_cours_enseignant(request):
    """
    This function likely retrieves a list of courses taught by a specific teacher.
    
    :param request: The parameter `request` typically refers to the HTTP request object that is sent to
    the server. In the context of a web application, it contains information about the request made by
    the client, such as the URL, headers, and any data sent in the request body. This parameter allows
    the view function
    """
    """View to list the lessons of a teacher"""
    if request.user.role != 'ENSEIGNANT':
        return redirect('login')
    
    try:
        enseignant = Enseignant.objects.get(user=request.user)
        
        # Cours de la semaine
        aujourd_hui = timezone.now().date()
        debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        fin_semaine = debut_semaine + timedelta(days=6)
        
        cours_semaine = Cours.objects.filter(
            enseignant=enseignant,
            date__range=[debut_semaine, fin_semaine]
        ).order_by('date', 'heure_debut')
        
        context = {
            'enseignant': enseignant,
            'cours_semaine': cours_semaine,
            'debut_semaine': debut_semaine,
            'fin_semaine': fin_semaine,
        }
        
        return render(request, 'liste_cours_enseignant.html', context)
        
    except Enseignant.DoesNotExist:
        messages.error(request, 'Teacher profile not found.')
        return redirect('login')

@login_required
def historique_presences(request):
    """
    This function likely retrieves a historical record of attendance or presence.
    
    :param request: The `request` parameter in the function `historique_presences` typically refers to
    an HTTP request object in web development frameworks like Django or Flask. This object contains
    information about the current request being made to the server, including data sent by the client,
    headers, and other relevant details. Developers use
    """
    """View for presence history"""
    if request.user.role not in ['ENSEIGNANT', 'ADMIN']:
        return redirect('login')
    
    # Filtres
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    classe_id = request.GET.get('classe')
    matiere_id = request.GET.get('matiere')
    
    # Base query
    if request.user.role == 'ENSEIGNANT':
        enseignant = Enseignant.objects.get(user=request.user)
        presences = Presence.objects.filter(session_appel__enseignant=enseignant)
    else:
        presences = Presence.objects.all()
    
    # Appliquer les filtres
    if date_debut:
        presences = presences.filter(session_appel__cours__date__gte=date_debut)
    if date_fin:
        presences = presences.filter(session_appel__cours__date__lte=date_fin)
    if classe_id:
        presences = presences.filter(session_appel__cours__classe_id=classe_id)
    if matiere_id:
        presences = presences.filter(session_appel__cours__matiere_id=matiere_id)
    
    # Pagination
    paginator = Paginator(presences.order_by('-session_appel__cours__date'), 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Options de filtres
    classes = Classe.objects.all()
    matieres = Matiere.objects.all()
    
    context = {
        'page_obj': page_obj,
        'classes': classes,
        'matieres': matieres,
        'filtres': {
            'date_debut': date_debut,
            'date_fin': date_fin,
            'classe_id': classe_id,
            'matiere_id': matiere_id,
        }
    }
    
    return render(request, 'historique_presences.html', context)

@login_required
def admin_course_management(request):
    """
    This function likely handles administrative tasks related to managing courses based on its name.
    
    :param request: The `request` parameter in the `admin_course_management` function is typically an
    object that contains information about the current HTTP request. This object allows you to access
    details such as the user making the request, any data being sent with the request, and other
    metadata related to the request. You can use
    """
    """View for the management of courses and their assignment to teachers"""
    if request.user.role != 'ADMIN':
        return redirect('login')
    
    try:
        # Récupérer tous les cours avec leurs détails
        cours = Cours.objects.select_related('matiere', 'classe', 'enseignant').all().order_by('date', 'heure_debut')
        
        # Récupérer tous les enseignants et matières pour le formulaire
        enseignants = Enseignant.objects.select_related('user').all()
        matieres = Matiere.objects.all()
        classes = Classe.objects.all()
        
        # Statistiques
        total_cours = cours.count()
        cours_aujourd_hui = cours.filter(date=timezone.now().date()).count()
        cours_sans_enseignant = cours.filter(enseignant__isnull=True).count()
        
        # Traitement des actions POST
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'create_course':
                # Créer un nouveau cours
                try:
                    matiere_id = request.POST.get('matiere')
                    classe_id = request.POST.get('classe')
                    enseignant_id = request.POST.get('enseignant')
                    date = request.POST.get('date')
                    heure_debut = request.POST.get('heure_debut')
                    heure_fin = request.POST.get('heure_fin')
                    salle = request.POST.get('salle', '')
                    
                    if not all([matiere_id, classe_id, enseignant_id, date, heure_debut, heure_fin]):
                        messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
                    else:
                        matiere = Matiere.objects.get(id=matiere_id)
                        classe = Classe.objects.get(id=classe_id)
                        enseignant = Enseignant.objects.get(id=enseignant_id)
                        
                        # Vérifier qu'il n'y a pas de conflit d'horaire
                        conflit = Cours.objects.filter(
                            classe=classe,
                            date=date,
                            heure_debut__lt=heure_fin,
                            heure_fin__gt=heure_debut
                        ).exists()
                        
                        if conflit:
                            messages.error(request, f'Conflit d\'horaire détecté pour la classe {classe.nom} le {date}.')
                        else:
                            Cours.objects.create(
                                matiere=matiere,
                                classe=classe,
                                enseignant=enseignant,
                                date=date,
                                heure_debut=heure_debut,
                                heure_fin=heure_fin,
                                salle=salle
                            )
                            messages.success(request, f'Cours {matiere.nom} - {classe.nom} créé avec succès !')
                            
                except Exception as e:
                    messages.error(request, f'Erreur lors de la création du cours: {str(e)}')
            
            elif action == 'assign_course':
                # Assigner un cours existant à un enseignant
                try:
                    cours_id = request.POST.get('cours_id')
                    enseignant_id = request.POST.get('enseignant_id')
                    
                    cours = Cours.objects.get(id=cours_id)
                    enseignant = Enseignant.objects.get(id=enseignant_id)
                    
                    cours.enseignant = enseignant
                    cours.save()
                    
                    messages.success(request, f'Cours {cours.matiere.nom} - {cours.classe.nom} assigné à {enseignant.user.get_full_name()}.')
                    
                except Exception as e:
                    messages.error(request, f'Erreur lors de l\'assignation: {str(e)}')
            
            elif action == 'delete_course':
                # Supprimer un cours
                try:
                    cours_id = request.POST.get('cours_id')
                    cours = Cours.objects.get(id=cours_id)
                    cours_nom = f"{cours.matiere.nom} - {cours.classe.nom}"
                    cours.delete()
                    messages.success(request, f'Cours {cours_nom} supprimé avec succès.')
                    
                except Exception as e:
                    messages.error(request, f'Erreur lors de la suppression: {str(e)}')
            
            elif action == 'create_class':
                # Créer une nouvelle classe
                try:
                    class_name = request.POST.get('class_name')
                    class_level = request.POST.get('class_level')
                    class_capacity = request.POST.get('class_capacity')
                    class_description = request.POST.get('class_description', '')
                    
                    if not all([class_name, class_level]):
                        messages.error(request, 'Le nom et le niveau de la classe sont obligatoires.')
                    else:
                        # Vérifier que la classe n'existe pas déjà
                        if Classe.objects.filter(nom=class_name).exists():
                            messages.error(request, f'Une classe avec le nom "{class_name}" existe déjà.')
                        else:
                            # Créer la classe avec le bon format
                            classe = Classe.objects.create(
                                nom=class_name,
                                capacite=class_capacity if class_capacity else 30,
                                annee_scolaire="2024-2025"  # Année scolaire actuelle
                            )
                            messages.success(request, f'Classe "{class_name}" créée avec succès !')
                            
                except Exception as e:
                    messages.error(request, f'Erreur lors de la création de la classe: {str(e)}')
            
            # Rediriger pour éviter la soumission multiple
            return redirect('admin_course_management')
        
        # Pagination des cours
        paginator = Paginator(cours, 20)  # 20 cours par page
        page_number = request.GET.get('page')
        cours_page = paginator.get_page(page_number)
        
        # Date d'aujourd'hui pour le template
        today = timezone.now().date()
        
        context = {
            'cours_page': cours_page,  # Variable paginée pour le template
            'cours': cours,  # Garder la liste complète pour les statistiques
            'enseignants': enseignants,
            'matieres': matieres,
            'classes': classes,
            'total_cours': total_cours,
            'cours_aujourd_hui': cours_aujourd_hui,
            'cours_sans_enseignant': cours_sans_enseignant,
            'today': today,  # Date d'aujourd'hui pour le template
        }
        
        return render(request, 'admin_course_management.html', context)
        
    except Exception as e:
        messages.error(request, f'Erreur: {str(e)}')
        return redirect('admin_dashboard')

@login_required
def mobile_qr_scanner(request, session_id):
    """
    This function is likely designed to handle a mobile QR code scanning request with a specific session
    ID.
    
    :param request: The `request` parameter typically refers to the HTTP request object that contains
    information about the incoming request, such as headers, parameters, and data. It is commonly used
    in web development frameworks to handle and process incoming requests from clients
    :param session_id: The `session_id` parameter in the `mobile_qr_scanner` function likely refers to a
    unique identifier for the current session or interaction. This identifier can be used to track and
    manage the session-specific data or state within the QR code scanning process. It helps in
    maintaining the context and continuity of
    """
    """View for the mobile interface of Scan QR"""
    if request.user.role != 'ENSEIGNANT':
        return redirect('login')
    
    try:
        # Récupérer la session d'appel
        session_appel = get_object_or_404(SessionAppel, id=session_id, enseignant__user=request.user)
        cours = session_appel.cours
        
        context = {
            'session_id': session_id,
            'cours': cours,
        }
        
        return render(request, 'mobile_qr_scanner.html', context)
        
    except SessionAppel.DoesNotExist:
        messages.error(request, 'Session d\'appel non trouvée.')
        return redirect('enseignant_dashboard')
    except Exception as e:
        messages.error(request, f'Erreur: {str(e)}')
        return redirect('enseignant_dashboard')


def mobile_checkin(request, eleve_id, cours_id, session_id):
    """
    This function is likely used for mobile check-in for a student (eleve) in a specific course (cours)
    session.
    
    :param request: The `request` parameter typically refers to the HTTP request object that is sent to
    the server when a client (such as a web browser or a mobile app) makes a request to a web server. It
    contains information about the request being made, such as headers, parameters, and data
    :param eleve_id: eleve_id is the unique identifier for the student or user who is checking in using
    the mobile app
    :param cours_id: The `cours_id` parameter typically refers to the unique identifier of a course. It
    is used to specify which course the check-in operation is being performed for. This parameter helps
    in identifying and processing the check-in request for a specific course within the system
    :param session_id: The `mobile_checkin` function seems to be related to checking in a student for a
    course session using a mobile device. The parameters provided are:
    """
    """
    Mobile check-in page to validate the presence of a student
    """
    try:
        # Récupérer les objets nécessaires
        eleve = get_object_or_404(Eleve, id=eleve_id)
        cours = get_object_or_404(Cours, id=cours_id)
        session_appel = get_object_or_404(SessionAppel, id=session_id)
        
        # Vérifier que la session correspond au cours
        if session_appel.cours != cours:
            messages.error(request, 'Session d\'appel invalide pour ce cours.')
            return redirect('home')
        
        # Récupérer ou créer la présence
        presence, created = Presence.objects.get_or_create(
            eleve=eleve,
            session_appel=session_appel,
            defaults={'statut': 'ABSENT'}
        )
        
        context = {
            'eleve': eleve,
            'cours': cours,
            'session_appel': session_appel,
            'presence': presence,
        }
        
        return render(request, 'mobile_checkin.html', context)
        
    except Exception as e:
        messages.error(request, f'Erreur lors du chargement de la page de check-in: {str(e)}')
        return redirect('home')


@require_http_methods(["POST"])
@csrf_exempt
def api_mobile_checkin(request):
    """
    This function is likely used for mobile check-in functionality in an API.
    
    :param request: The `request` parameter in the `api_mobile_checkin` function is typically an object
    that contains information about the incoming HTTP request made to the API. This object usually
    includes details such as the request method (GET, POST, etc.), headers, parameters, and body data.
    Developers can access and
    """
    """
    API to confirm the presence from the mobile interface
    """
    try:
        data = json.loads(request.body)
        eleve_id = data.get('eleve_id')
        session_id = data.get('session_id')
        cours_id = data.get('cours_id')
        statut = data.get('statut', 'PRESENT')
        
        # Récupérer les objets
        eleve = get_object_or_404(Eleve, id=eleve_id)
        session_appel = get_object_or_404(SessionAppel, id=session_id)
        cours = get_object_or_404(Cours, id=cours_id)
        
        # Vérifier la cohérence
        if session_appel.cours != cours:
            return JsonResponse({
                'success': False,
                'error': 'Session d\'appel invalide pour ce cours'
            })
        
        # Mettre à jour ou créer la présence
        presence, created = Presence.objects.get_or_create(
            eleve=eleve,
            session_appel=session_appel,
            defaults={
                'statut': statut,
                'heure_arrivee': timezone.now(),
                'methode_detection': 'QR_CODE'
            }
        )
        
        if not created:
            # Mettre à jour une présence existante
            presence.statut = statut
            presence.heure_arrivee = timezone.now()
            presence.methode_detection = 'QR_CODE'
            presence.save()
        
        # Envoyer un email au parent selon le statut
        from .email_service import ParentNotificationService
        
        if statut == 'PRESENT':
            # Envoyer un email de confirmation de présence
            ParentNotificationService.send_presence_confirmation_email(presence.id)
        elif statut == 'RETARD':
            # Envoyer un email de notification de retard
            ParentNotificationService.send_retard_notification_email(presence.id)
        elif statut == 'ABSENT':
            # Envoyer un email de notification d'absence
            ParentNotificationService.send_absence_notification_email(presence.id)
        
        return JsonResponse({
            'success': True,
            'message': f'Présence confirmée pour {eleve.user.get_full_name()}',
            'eleve_name': eleve.user.get_full_name(),
            'statut': statut,
            'heure_arrivee': presence.heure_arrivee.strftime('%H:%M')
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Données JSON invalides'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["GET"])
def api_check_presence_status(request):
    """
    This function is likely used to check the presence status of a user in an API.
    
    :param request: The `request` parameter in the `api_check_presence_status` function likely refers to
    the HTTP request object that contains information about the incoming request, such as headers,
    parameters, and body content. This parameter is commonly used in web development to handle and
    process incoming requests from clients
    """
    """
    API to verify the presence status of a student
    """
    try:
        eleve_id = request.GET.get('eleve_id')
        session_id = request.GET.get('session_id')
        
        if not eleve_id or not session_id:
            return JsonResponse({
                'success': False,
                'error': 'Paramètres manquants'
            })
        
        # Récupérer la présence
        try:
            presence = Presence.objects.get(
                eleve_id=eleve_id,
                session_appel_id=session_id
            )
            return JsonResponse({
                'success': True,
                'status': presence.statut,
                'heure_arrivee': presence.heure_arrivee.strftime('%H:%M') if presence.heure_arrivee else None
            })
        except Presence.DoesNotExist:
            return JsonResponse({
                'success': True,
                'status': 'ABSENT',
                'heure_arrivee': None
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["GET"])
def api_check_session_updates(request):
    """
    This function is likely used to check for updates in a session within an API.
    
    :param request: The `request` parameter in the `api_check_session_updates` function likely refers to
    an HTTP request object that contains information about the incoming request, such as headers,
    parameters, and data. This parameter is used to handle and process the request sent to the API
    endpoint
    """
    """
    API to check the presence updates in a session
    """
    try:
        session_id = request.GET.get('session_id')
        last_check = request.GET.get('last_check')
        
        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'Session ID manquant'
            })
        
        # Récupérer la session
        session_appel = get_object_or_404(SessionAppel, id=session_id)
        
        # Construire la requête de base
        presences_query = Presence.objects.filter(session_appel=session_appel)
        
        # Si un timestamp de dernière vérification est fourni, filtrer les mises à jour récentes
        if last_check:
            try:
                last_check_time = timezone.datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                presences_query = presences_query.filter(
                    updated_at__gt=last_check_time
                )
            except (ValueError, TypeError):
                # Si le timestamp est invalide, ignorer le filtre
                pass
        
        # Récupérer les présences mises à jour
        presences = presences_query.select_related('eleve__user').order_by('-updated_at')
        
        updates = []
        for presence in presences:
            updates.append({
                'eleve_id': presence.eleve.id,
                'eleve_name': presence.eleve.user.get_full_name(),
                'statut': presence.statut,
                'heure_arrivee': presence.heure_arrivee.strftime('%H:%M') if presence.heure_arrivee else None,
                'updated_at': presence.updated_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'updates': updates,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["POST"])
@csrf_exempt
def api_notify_teacher_redirect(request):
    """
    This function is likely used to notify a teacher via an API and then redirect the request.
    
    :param request: The `request` parameter in the `api_notify_teacher_redirect` function is typically
    an object that represents the HTTP request made to the server. It contains information such as the
    request method, headers, body, and other relevant data that can be used to process and respond to
    the request
    """
    """
    API to notify the teacher that a presence has been confirmed and trigger a redirection
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        cours_id = data.get('cours_id')
        eleve_id = data.get('eleve_id')
        action = data.get('action')
        
        if not all([session_id, cours_id, eleve_id, action]):
            return JsonResponse({'success': False, 'error': 'Paramètres manquants'}, status=400)
        
        # Stocker la notification pour que le PC puisse la récupérer
        # On utilise une approche simple avec un fichier temporaire ou session
        notification_data = {
            'session_id': session_id,
            'cours_id': cours_id,
            'eleve_id': eleve_id,
            'action': action,
            'timestamp': timezone.now().isoformat()
        }
        
        # Pour simplifier, on stocke dans la session Django
        # En production, on utiliserait Redis ou une base de données
        request.session[f'teacher_notification_{session_id}'] = notification_data
        
        return JsonResponse({
            'success': True,
            'message': 'Notification envoyée à l\'enseignant'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_authenticate_teacher(request):
    """
    This function is likely used to authenticate a teacher accessing an API.
    
    :param request: The `request` parameter in the `api_authenticate_teacher` function likely refers to
    an HTTP request object that contains information about the incoming request, such as headers,
    parameters, and data. This parameter is commonly used in web development to handle and process
    incoming requests from clients
    """
    """
    API to authenticate a teacher and verify that he is allowed for the course
    """
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        cours_id = data.get('cours_id')
        expected_teacher_id = data.get('expected_teacher_id')
        
        if not all([email, password, cours_id, expected_teacher_id]):
            return JsonResponse({'success': False, 'error': 'Paramètres manquants'}, status=400)
        
        # Authentifier l'utilisateur
        user = authenticate(request, username=email, password=password)
        
        if user is None:
            return JsonResponse({
                'success': False, 
                'error': 'Identifiants incorrects'
            })
        
        # Vérifier que l'utilisateur est un enseignant
        if user.role != 'ENSEIGNANT':
            return JsonResponse({
                'success': False, 
                'error': 'Accès refusé : vous n\'êtes pas un enseignant'
            })
        
        # Vérifier que l'enseignant est bien celui du cours
        if user.enseignant.id != expected_teacher_id:
            return JsonResponse({
                'success': False, 
                'error': 'Accès refusé : vous n\'êtes pas l\'enseignant de ce cours'
            })
        
        # Authentification réussie
        return JsonResponse({
            'success': True,
            'teacher_name': user.get_full_name(),
            'teacher_id': user.enseignant.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_log_unauthorized_access(request):
    """
    This function logs unauthorized access to an API.
    
    :param request: The `request` parameter in the `api_log_unauthorized_access` function likely refers
    to the HTTP request object that contains information about the incoming request, such as headers,
    parameters, and other relevant data. This parameter is used to log unauthorized access attempts to
    an API, allowing you to track and monitor
    """
    """
    API to record unauthorized attempts
    """
    try:
        data = json.loads(request.body)
        email = data.get('email')
        cours_id = data.get('cours_id')
        session_id = data.get('session_id')
        reason = data.get('reason')
        timestamp = data.get('timestamp')
        
        # Enregistrer dans les logs (ici on utilise print, en production on utiliserait un système de logs)
        print(f"TENTATIVE D'ACCÈS NON AUTORISÉE:")
        print(f"  - Email: {email}")
        print(f"  - Cours ID: {cours_id}")
        print(f"  - Session ID: {session_id}")
        print(f"  - Raison: {reason}")
        print(f"  - Timestamp: {timestamp}")
        print(f"  - IP: {request.META.get('REMOTE_ADDR', 'Unknown')}")
        print("-" * 50)
        
        # En production, on pourrait aussi enregistrer dans une base de données
        # ou envoyer une alerte à l'administrateur
        
        return JsonResponse({
            'success': True,
            'message': 'Tentative d\'accès enregistrée'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_finish_call(request):
    """
    This function is likely used to handle the completion of an API call in a Python application.
    
    :param request: The `request` parameter in the `api_finish_call` function likely refers to the
    request object that contains information about the incoming API call. This object typically includes
    details such as the request method, headers, parameters, and body data. You can access and process
    this information within the function to handle the
    """
    """
    API to end a call and update the status of the session
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        cours_id = data.get('cours_id')
        
        if not session_id or not cours_id:
            return JsonResponse({'success': False, 'error': 'Paramètres manquants'}, status=400)
        
        # Récupérer la session d'appel
        session_appel = get_object_or_404(SessionAppel, id=session_id)
        
        # Vérifier que la session correspond au cours
        if session_appel.cours.id != cours_id:
            return JsonResponse({'success': False, 'error': 'Session ne correspond pas au cours'}, status=400)
        
        # Mettre à jour le statut de la session
        session_appel.statut = 'TERMINE'
        session_appel.date_fin = timezone.now()
        session_appel.save()
        
        # Calculer les statistiques finales
        presences = Presence.objects.filter(session_appel=session_appel)
        present_count = presences.filter(statut='PRESENT').count()
        retard_count = presences.filter(statut='RETARD').count()
        absent_count = presences.filter(statut='ABSENT').count()
        
        return JsonResponse({
            'success': True,
            'message': 'Appel terminé avec succès',
            'stats': {
                'present': present_count,
                'retard': retard_count,
                'absent': absent_count,
                'total': presences.count()
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# Feedback views
@login_required
def feedback_create(request):
    """Vue pour créer un nouveau feedback"""
    if request.user.role != 'PARENT':
        return redirect('login')
    
    try:
        parent = Parent.objects.get(user=request.user)
    except Parent.DoesNotExist:
        messages.error(request, 'Profil parent non trouvé.')
        return redirect('login')
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST, parent=parent)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.parent = parent
            feedback.save()
            
            # Return success modal instead of JSON
            return render(request, 'feedback/success_modal.html', {
                'feedback': feedback
            })
        else:
            # Return form with errors
            return render(request, 'feedback/modal_content.html', {
                'form': form,
                'parent': parent,
                'errors': form.errors
            })
    else:
        form = FeedbackForm(parent=parent)
    
    return render(request, 'feedback/modal_feedback.html', {
        'form': form,
        'parent': parent
    })

@login_required
def feedback_modal(request):
    """Vue pour récupérer le modal de feedback via AJAX"""
    if request.user.role != 'PARENT':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        parent = Parent.objects.get(user=request.user)
        form = FeedbackForm(parent=parent)
        
        return render(request, 'feedback/modal_content.html', {
            'form': form,
            'parent': parent
        })
        
    except Parent.DoesNotExist:
        return JsonResponse({'error': 'Parent profile not found'}, status=404)

@login_required
def feedback_list(request):
    """Vue pour lister les feedbacks du parent"""
    if request.user.role != 'PARENT':
        return redirect('login')
    
    try:
        parent = Parent.objects.get(user=request.user)
        feedbacks = Feedback.objects.filter(parent=parent).order_by('-date_creation')
        
        return render(request, 'feedback/feedback_list.html', {
            'feedbacks': feedbacks,
            'parent': parent
        })
        
    except Parent.DoesNotExist:
        messages.error(request, 'Profil parent non trouvé.')
        return redirect('login')

@login_required
def feedback_detail(request, feedback_id):
    """Vue pour voir les détails d'un feedback"""
    if request.user.role != 'PARENT':
        return redirect('login')
    
    try:
        parent = Parent.objects.get(user=request.user)
        feedback = get_object_or_404(Feedback, id=feedback_id, parent=parent)
        
        return render(request, 'feedback/feedback_detail.html', {
            'feedback': feedback,
            'parent': parent
        })
        
    except Parent.DoesNotExist:
        messages.error(request, 'Profil parent non trouvé.')
        return redirect('login')
