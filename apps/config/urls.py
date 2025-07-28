# from django.conf.urls import handler403
from django.conf import settings
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views.generic import TemplateView


handler403 = "config.views.custom_permission_denied_view"

urlpatterns = [
    # API and admin routes (keep Django)
    path("mgmt/", include("mgmt.urls")),
    path("tracking/", include("tracking.urls")),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("select2/", include("django_select2.urls")),
    # React app routes (catch-all for front-end)
    path("", TemplateView.as_view(template_name="react/index.html")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
