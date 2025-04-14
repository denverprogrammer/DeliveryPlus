import base64
import json
from django.contrib import admin, messages
from django.utils.html import format_html
from subadmin import SubAdmin, RootSubAdmin
from config import settings
from tracking.api import IpStackApiClient, TwilioApiClient, UserStackApiClient
from tracking.models import Campaign, TrackingData, Agent
from django.utils.timezone import localtime
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_datetime
from typing import Optional, Dict, Any
from ipware import get_client_ip
import pprint


# def get_client_ip(request) -> str:
#     pprint.pprint(request.META)
#     client_ip, is_routable = get_client_ip(request)
#     if client_ip is None:
#         return None
#     elif is_routable:
#         # The client's IP address is publicly routable on the Internet
#         return client_ip
#     else:
#         # The client's IP address is private
#         return client_ip


def get_tracking_header(request) -> Dict[str, Any]:
    # 1. Get the header
    

    try:
        header_value = request.headers.get('x-tracking-payload', None)
        
        if header_value is None:
            raise Exception('No header sent')
        
        # 2. Base64-decode (ensure padding is correct)
        decoded_bytes = base64.b64decode(header_value + '===')
        decoded_str = decoded_bytes.decode('utf-8')

        # 3. Parse JSON
        return json.loads(decoded_str)
    except (ValueError, json.JSONDecodeError, base64.binascii.Error) as e: # type: ignore
        print('no tracking headers sent')
    return { 'message' : 'no tracking headers sent'}


@csrf_exempt
def track_view(request: HttpRequest, token: Optional[str] = None) -> HttpResponse:

    if token and request.method == 'POST':
        agent = get_object_or_404(Agent, token=token)
        http_method = request.POST.get('http_method', request.method)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user_agent_data = { 'ua' : user_agent, 'messasge' : 'N/A' }
        ip_address, is_routable = get_client_ip(request)
        ip_data = { 'ip_address': ip_address, 'message': 'ip address is private' }
        tracking_data = getattr(request, 'tracking_payload', { 'message' : 'no tracking data' })
        headers_data = get_tracking_header(request)
        
        if ip_address and is_routable:
            ipStackClient = IpStackApiClient(settings.IP_STACK_KEY)
            ip_data = ipStackClient.get_data(ip_address)
            
        if user_agent:
            userstack_client = UserStackApiClient(api_key=settings.USER_STACK_KEY)
            user_agent_data = userstack_client.get_data(user_agent) if user_agent else None

        TrackingData.objects.create(
            agent=agent,
            http_method=http_method,
            tracking_data=tracking_data,
            ip_data = ip_data,
            user_agent_data=user_agent_data,
            headers_data=headers_data,
            form_data=json.dumps(request.POST)
            # phone_data={ 'messasge' : 'N/A' }
        )
        return JsonResponse({
            'status': 'success', 
            'message': '✅ Your package was picked up by a local carrier. It may take a few hours to arrive at the sorting facility.'
        })

    # For GET request: serve Django template
    return render(request, 'tracking/track.html', {})

@csrf_exempt
def redirect_package_view(request, token: Optional[str] = None) -> HttpResponse:

    if token and request.method == 'POST':
        agent = get_object_or_404(Agent, token=token)
        http_method = request.POST.get('http_method', request.method)
        notifications = request.POST.get('notifications')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user_agent_data = { 'ua' : user_agent, 'messasge' : 'N/A' }
        ip_address, is_routable = get_client_ip(request)
        ip_data = { 'ip_address': ip_address, 'message': 'ip address is private' }
        tracking_data = getattr(request, 'tracking_payload', { 'message' : 'no tracking data' })
        headers_data = get_tracking_header(request)
        # phone_data = { 'messasge' : 'no phone number given or invalid' }

        if ip_address and is_routable:
            ip_stack_client = IpStackApiClient(settings.IP_STACK_KEY)
            ip_data = ip_stack_client.get_data(ip_address)
            
        if user_agent:
            userstack_client = UserStackApiClient(api_key=settings.USER_STACK_KEY)
            user_agent_data = userstack_client.get_data(user_agent) if user_agent else None

        # if notifications:
        #     twilio_client = TwilioApiClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        #     phone_data = twilio_client.get_data(notifications) if notifications else None

        # agent.save(update_fields=[
        #     'street_address', 'city', 'state', 'zip_code', 'country', 'notifications'
        # ])

        TrackingData.objects.create(
            agent=agent,
            http_method=http_method,
            tracking_data=tracking_data,
            ip_data = ip_data,
            user_agent_data=user_agent_data,
            headers_data=headers_data,
            form_data=json.dumps(request.POST)
            # phone_data=phone_data
        )

        return JsonResponse({
            'status': 'success', 
            'message': '✅ A request was sent to redirect your package.  Please check your phone for updates we have sent you.'
        })

    return render(request, 'tracking/redirect.html', {})
