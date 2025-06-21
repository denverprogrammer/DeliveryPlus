# from django.conf.urls import handler403
from config import views
from django.conf import settings
from django.contrib import admin
from django.urls import include
from django.urls import path


handler403 = "config.views.custom_permission_denied_view"

urlpatterns = [
    path("mgmt/", include("mgmt.urls")),
    path("tracking/", include("tracking.urls")),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("select2/", include("django_select2.urls")),
    path("", views.home_page_view, name="home"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
