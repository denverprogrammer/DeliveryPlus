from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler403

handler403 = "config.views.custom_permission_denied_view"

urlpatterns = [
    path('', include('delivery.urls')),
    path('', include("tracking.urls")),
    path('admin/', admin.site.urls)
]