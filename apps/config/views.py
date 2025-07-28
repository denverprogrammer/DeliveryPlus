from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse


def custom_permission_denied_view(
    request: HttpRequest, exception: PermissionDenied
) -> HttpResponse:
    return JsonResponse({"error": "Permission denied"}, status=403)
