from django.urls import path
from . import views

urlpatterns = [
    path('track/<str:token>/', views.track_view, name='track'),
    path('redirect/<str:token>/', views.redirect_package_view, name='redirect'),
    path('tracking-data/<int:pk>/', views.tracking_data_modal, name='tracking_data_modal'),
]
