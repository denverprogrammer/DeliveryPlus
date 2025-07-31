from django.contrib import admin
from django.urls import path
from tracking.views import TagAutocomplete
from . import views


urlpatterns = [
    path("tracking-dialog/<int:pk>/", views.tracking_data_modal, name="tracking_data_dialog"),
    path(
        "admin/tag-autocomplete/",
        admin.site.admin_view(TagAutocomplete.as_view()),
        name="tag-autocomplete",
    ),
]
