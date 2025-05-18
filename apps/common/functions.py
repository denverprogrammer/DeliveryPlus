from common.types import (
    IPGeolocationResponse,
    IpData,
    LocaleData,
    LocationData,
    TimeData,
    UserAgentData,
)
from config.common import IpAddressInfo, LocationInfo, HeaderData
from config import settings
from common.api import IPGeolocationApiClient, UserStackApiClient, VpnApiClient
from tracking.common import TrackingType
from django.http import HttpRequest
from typing import Optional
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def get_ip_data(request: HttpRequest, header_data: HeaderData) -> IpData:
    """Extract and process IP data from request and headers."""
    # Get IP from headers (ipinfo.io and ipware)
    header_address: Optional[IpAddressInfo] = header_data.getHeaderIpAddress()
    server_address: Optional[IpAddressInfo] = header_data.getClientIpAddress(request)

    header_info: Optional[IPGeolocationResponse] = None
    server_info: Optional[IPGeolocationResponse] = None

    # Get IP data from Ip Geolocation Api
    ip_client = IPGeolocationApiClient(settings.IP_GEO_LOCATION_KEY)
    # Get VPN data from VPN Api
    vpn_client = VpnApiClient(settings.VPN_API_IO_KEY)

    # Always use header IP if available, otherwise fall back to server IP
    if header_address and header_address.address and header_address.is_routable:
        header_info = ip_client.get_data(header_address.address)

    if header_info:
        vpn_data = vpn_client.get_data(header_info.ip)
        header_info.security = vpn_data.security if vpn_data else None

    if server_address and server_address.address and server_address.is_routable:
        server_info = ip_client.get_data(server_address.address)

    if server_info:
        vpn_data = vpn_client.get_data(server_info.ip)
        server_info.security = vpn_data.security if vpn_data else None

    ip_data = IpData(server=server_info, header=header_info, selected=None, source=None, info=None)

    if header_info and header_info.ip:
        ip_data.selected = header_info
        ip_data.source = TrackingType.HEADER
    elif server_info and server_info.ip:
        ip_data.selected = server_info
        ip_data.source = TrackingType.SERVER

    return ip_data


def get_user_agent_data(request: HttpRequest, header_data: HeaderData) -> UserAgentData:
    """Extract and process user agent data from request."""
    # Get user agent from different sources
    server_user_agent: str = request.META.get("HTTP_USER_AGENT", "")
    header_user_agent: str = header_data.navigator.user_agent

    # Store both user agents in the data
    user_agent_data = UserAgentData(
        server=server_user_agent, header=header_user_agent, selected=None, source=None, info=None
    )

    if header_user_agent:
        user_agent_data.selected = header_user_agent
        user_agent_data.source = TrackingType.HEADER
    elif server_user_agent:
        user_agent_data.selected = server_user_agent
        user_agent_data.source = TrackingType.SERVER

    # Add selected user agent information
    if user_agent_data.selected:
        # Get user agent data from UserStack
        userstack_client = UserStackApiClient(api_key=settings.USER_STACK_KEY)
        user_agent_data.info = userstack_client.get_data(user_agent_data.selected)

    return user_agent_data


def get_locale_data(request: HttpRequest, header_data: HeaderData) -> LocaleData:
    """Extract and process locale data from request and headers."""
    # Get locale from different sources
    server_locale: str = request.META.get("HTTP_ACCEPT_LANGUAGE", ",").split(",")[0]
    header_locale: str = header_data.navigator.language

    # Store both locales in the data
    locale_data = LocaleData(
        server=server_locale, header=header_locale, selected=None, source=None, info=None
    )

    # Always use header locale if available, otherwise fall back to server locale

    if locale_data.header:
        locale_data.selected = header_locale
        locale_data.source = TrackingType.HEADER
    elif locale_data.server:
        locale_data.selected = server_locale
        locale_data.source = TrackingType.SERVER

    return locale_data


def get_time_data(header_data: HeaderData, ip_data: IpData) -> TimeData:
    """Extract and process time and timezone data from request, headers, and IP data."""
    # Get timezone
    timestamp: int = header_data.getTimestamp()
    header_timezone: Optional[str] = header_data.getTimezone()
    ip_timezone: Optional[str] = ip_data.getTimezone()

    # Store time data
    time_data = TimeData(
        header=header_timezone, server=ip_timezone, selected=None, source=None, info=None
    )

    if header_timezone:
        time_data.source = TrackingType.HEADER
        time_data.selected = header_timezone
    elif ip_timezone:
        time_data.source = TrackingType.SERVER
        time_data.selected = ip_timezone

    if time_data.selected:
        client_time = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
        time_data.info = client_time.astimezone(ZoneInfo(time_data.selected))

    return time_data


def get_location_data(header_data: HeaderData, ip_data: IpData) -> LocationData:
    """Extract and process location data from request, headers, and IP data."""

    header_location: Optional[LocationInfo] = header_data.getLocation()
    ip_location: Optional[LocationInfo] = ip_data.getLocation()

    # Store both locations in the data
    location_data = LocationData(
        header=header_location, server=ip_location, selected=None, source=None
    )

    if header_location:
        location_data.selected = header_location
        location_data.source = TrackingType.HEADER
    elif ip_location:
        location_data.selected = ip_location
        location_data.source = TrackingType.SERVER

    return location_data
