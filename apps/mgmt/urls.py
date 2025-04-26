from django.urls import path
from . import views

urlpatterns = [
    path('company/edit/', views.edit_company_view, name='edit_company'),
    
    path('agents/add/', views.agent_create_view, name='agent_add'),
    path('agents/<int:agent_id>/edit/', views.agent_edit_view, name='agent_edit'),
    path('agents/', views.agent_list_view, name='agent_list'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard_view, name='dashboard'),
]
