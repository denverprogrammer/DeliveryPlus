from django.urls import path
from . import views
from tagulous.views import autocomplete  # type: ignore[attr-defined]

urlpatterns = [
    path("tracking-dialog/<int:pk>/", views.tracking_data_modal, name="tracking_data_dialog"),
    path("redirects/<str:token>/", views.redirect_package_view, name="package_redirect_token"),
    path("redirects/", views.redirect_package_view, name="package_redirect"),
    path("<str:token>/", views.track_view, name="package_tracking_token"),
    path(
        "agent-tags/autocomplete/",
        autocomplete,  # type: ignore[attr-defined]
        {"model": "tracking.AgentTag"},
        name="agent_tags_autocomplete",
    ),
    path("", views.track_view, name="package_tracking"),
]
