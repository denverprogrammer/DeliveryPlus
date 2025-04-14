from django.urls import path
from . import views

urlpatterns = [
    path('redirects', views.redirect_package_view, name='package_redirect'),
    path('redirects/<str:token>', views.redirect_package_view, name='package_redirect_token'),
    path('tracking', views.track_view, name='package_tracking'),
    path('tracking/<str:token>', views.track_view, name='package_tracking_token'),
]