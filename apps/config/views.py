from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render


def custom_permission_denied_view(
    request: HttpRequest, exception: PermissionDenied
) -> HttpResponse:
    return render(request, "403.html", status=403)


def home_page_view(request: HttpRequest) -> HttpResponse:
    return render(request, "config/index.html")
