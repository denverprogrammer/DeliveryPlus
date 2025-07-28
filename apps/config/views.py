from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.generic import TemplateView


def custom_permission_denied_view(
    request: HttpRequest, exception: PermissionDenied
) -> HttpResponse:
    return JsonResponse({"error": "Permission denied"}, status=403)


class HostBasedView(TemplateView):
    """Serve different content based on the host header."""

    def get_template_names(self) -> list[str]:
        host = self.request.get_host().lower()

        if host.startswith("admin."):
            # For admin domain, serve Django admin
            return ["admin/login.html"]  # This will redirect to admin login
        else:
            # For other domains, serve React app
            return ["react/index.html"]

    def get(self, request: HttpRequest, *args: tuple, **kwargs: dict) -> HttpResponse:
        host = request.get_host().lower()

        if host.startswith("admin."):
            # Redirect to Django admin
            from django.shortcuts import redirect

            return redirect("/admin/")
        else:
            # Serve React app
            return super().get(request, *args, **kwargs)
