from django.urls import path
from . import views

urlpatterns = [
    path('enseignant/appels/', views.teacher_attendance_today, name='teacher_attendance_today'),
    path('enseignant/matieres/', views.teacher_subjects, name='teacher_subjects'),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('enseignant/dashboard/', views.enseignant_dashboard, name='enseignant_dashboard'),
    path('eleve/dashboard/', views.eleve_dashboard, name='eleve_dashboard'),
    path('parent/dashboard/', views.parent_dashboard, name='parent_dashboard'),
    
    # Reconnaissance faciale
    path('qr-code-scan/<int:cours_id>/', views.qr_code_scan, name='qr_code_scan'),
    path('mobile-qr-scanner/<int:session_id>/', views.mobile_qr_scanner, name='mobile_qr_scanner'),
    path('api/qr-code-scan/', views.api_qr_code_scan, name='api_qr_code_scan'),
    path('api/mobile-qr-scan/', views.api_mobile_qr_scan, name='api_mobile_qr_scan'),
    
    # API pour la gestion des présences
    path('api/update-presence/', views.api_update_presence, name='api_update_presence'),
    path('api/update-presence-from-scan/', views.api_update_presence_from_scan, name='api_update_presence_from_scan'),
    path('api/validate-session/', views.api_validate_session, name='api_validate_session'),
    
    # Gestion des cours et présences
    path('enseignant/cours/', views.liste_cours_enseignant, name='liste_cours_enseignant'),
    path('historique-presences/', views.historique_presences, name='historique_presences'),

    # URLs Admin
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/create/', views.admin_create_user, name='admin_create_user'),
    path('admin/users/api/', views.admin_get_users, name='admin_get_users'),
    path('admin/users/<int:user_id>/toggle-status/', views.admin_toggle_user_status, name='admin_toggle_user_status'),
    path('admin/users/<int:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
    path('admin/users/<int:user_id>/details/', views.admin_get_user_details, name='admin_get_user_details'),
    path('admin/users/<int:user_id>/update/', views.admin_update_user, name='admin_update_user'),

    path('admin/courses/', views.admin_course_management, name='admin_course_management'),
    path('admin/schedule/', views.admin_schedule, name='admin_schedule'),
    path('admin/attendance/', views.admin_attendance, name='admin_attendance'),
    path('admin/stats/', views.admin_stats, name='admin_stats'),
    path('admin/feedback/', views.admin_feedback, name='admin_feedback'),
    path('admin/notifications/', views.admin_notifications, name='admin_notifications'),
    path('admin/export/', views.admin_export, name='admin_export'),
    path('admin/settings/', views.admin_settings, name='admin_settings'),

    # URLs Enseignant
    path('enseignant/classes/', views.teacher_classes, name='teacher_classes'),
    path('enseignant/scan-qr-eleves/<int:cours_id>/', views.scan_qr_eleves, name='scan_qr_eleves'),
    
    # Mobile check-in
    path('mobile-checkin/<int:eleve_id>/<int:cours_id>/<str:session_id>/', views.mobile_checkin, name='mobile_checkin'),
    
    # API endpoints
    path('api/mobile-checkin/', views.api_mobile_checkin, name='api_mobile_checkin'),
    path('api/check-presence-status/', views.api_check_presence_status, name='api_check_presence_status'),
    path('api/check-session-updates/', views.api_check_session_updates, name='api_check_session_updates'),
    path('api/notify-teacher-redirect/', views.api_notify_teacher_redirect, name='api_notify_teacher_redirect'),
    path('api/authenticate-teacher/', views.api_authenticate_teacher, name='api_authenticate_teacher'),
    path('api/log-unauthorized-access/', views.api_log_unauthorized_access, name='api_log_unauthorized_access'),
    path('api/finish-call/', views.api_finish_call, name='api_finish_call'),
]