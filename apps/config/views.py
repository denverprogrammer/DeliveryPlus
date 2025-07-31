from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.generic import View


def custom_permission_denied_view(
    request: HttpRequest, exception: PermissionDenied
) -> HttpResponse:
    return JsonResponse({"error": "Permission denied"}, status=403)


class HostBasedView(View):
    """Serve different content based on the host header."""

    def get(self, request: HttpRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
        host = request.get_host().lower()

        if host.startswith("admin."):
            # Redirect to Django admin
            from django.shortcuts import redirect

            return redirect("/admin/")
        else:
            # Serve React build files directly
            import os
            from django.conf import settings

            react_index_path = os.path.join(settings.STATIC_ROOT, "react", "index.html")
            if os.path.exists(react_index_path):
                with open(react_index_path, "r") as f:
                    return HttpResponse(f.read(), content_type="text/html")
            else:
                return HttpResponse("React app not built yet", status=404)
