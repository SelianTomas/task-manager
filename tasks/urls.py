from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Hlavné stránky
    path('', views.task_list, name='task_list'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # CRUD operácie pre úlohy
    path('new/', views.task_create, name='task_create'),
    path('<int:pk>/edit/', views.task_update, name='task_update'),
    path('<int:pk>/delete/', views.task_delete, name='task_delete'),

    # Akcie s úlohami
    path('<int:pk>/toggle-status/', views.task_toggle_status, name='task_toggle_status'),

    # API endpoints
    path('api/stats/', views.task_stats_api, name='task_stats_api'),

    # Autentifikácia (ak nie je cez allauth)
    path('register/', views.register, name='register'),
]