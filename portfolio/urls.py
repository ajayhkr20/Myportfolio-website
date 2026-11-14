from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact_submit, name='contact_submit'),
    path('resume/download/', views.download_resume, name='download_resume'),
    path('chatbot/', views.chatbot_stream, name='chatbot_stream'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/profile/', views.manage_profile, name='manage_profile'),
    path('dashboard/skills/', views.skill_manager, name='skill_manager'),
    path('dashboard/skills/add/', views.skill_create, name='skill_create'),
    path('dashboard/skills/<int:pk>/edit/', views.skill_edit, name='skill_edit'),
    path('dashboard/skills/<int:pk>/delete/', views.skill_delete, name='skill_delete'),
    path('dashboard/messages/', views.message_list, name='message_list'),
    path('dashboard/messages/<int:pk>/', views.message_detail, name='message_detail'),
    path('dashboard/messages/<int:pk>/delete/', views.message_delete, name='message_delete'),
    path('dashboard/visitors/', views.visitor_list, name='visitor_list'),
    path('dashboard/visitors/block/', views.toggle_visitor_block, name='toggle_visitor_block'),
    path('dashboard/users/', views.user_list, name='user_list'),
    path('dashboard/users/add/', views.user_create, name='user_create'),
    path('dashboard/users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('dashboard/users/<int:pk>/delete/', views.user_delete, name='user_delete'),

    path('dashboard/<str:model_name>/', views.crud_list, name='crud_list'),
    path('dashboard/<str:model_name>/add/', views.crud_create, name='crud_create'),
    path('dashboard/<str:model_name>/<int:pk>/edit/', views.crud_edit, name='crud_edit'),
    path('dashboard/<str:model_name>/<int:pk>/delete/', views.crud_delete, name='crud_delete'),

    path('login/', auth_views.LoginView.as_view(template_name='portfolio/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]