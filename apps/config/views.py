from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.core.exceptions import PermissionDenied


def custom_permission_denied_view(
    request: HttpRequest, exception: PermissionDenied
) -> HttpResponse:
    return render(request, "403.html", status=403)


def home_page_view(request: HttpRequest) -> HttpResponse:
    return render(request, "config/index.html")
