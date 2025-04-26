from django.contrib import admin
from django.urls import path, include
# from django.conf.urls import handler403
from . import views

handler403 = "config.views.custom_permission_denied_view"

urlpatterns = [
    path('mgmt/', include('mgmt.urls')),
    path('tracking/', include('tracking.urls')),
    path('admin/', admin.site.urls),
    path('', views.home_page_view, name='home'),
]
