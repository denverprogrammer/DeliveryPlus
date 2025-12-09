from django.urls import path
from . import views


urlpatterns = [
    path("company/edit/", views.edit_company_view, name="edit_company"),
    path("recipients/add/", views.recipient_create_view, name="recipient_add"),
    path("recipients/<int:recipient_id>/edit/", views.recipient_edit_view, name="recipient_edit"),
    path("recipients/", views.recipient_list_view, name="recipient_list"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard_view, name="dashboard"),
]
