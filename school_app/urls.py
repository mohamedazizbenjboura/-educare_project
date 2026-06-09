from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/attendance/<int:student_id>/', views.log_attendance, name='log_attendance'),
    path('counselor/', views.counselor_dashboard, name='counselor_dashboard'),
    path('counselor/case/<int:case_id>/', views.case_detail, name='case_detail'),
    path('counselor/export/', views.export_cases_csv, name='export_cases_csv'),
    path('principal/', views.principal_dashboard, name='principal_dashboard'),
    path('counselor/config/', views.update_config, name='update_config'),
    path('api/stats/', views.api_school_stats, name='api_school_stats'),
]
