from django.urls import path
from . import views

urlpatterns = [
    path('package_redirect/<str:token>/', views.redirect_package_view, name='tracking'),
    path('tracking/<str:token>/', views.track_view, name='tracking'),
]