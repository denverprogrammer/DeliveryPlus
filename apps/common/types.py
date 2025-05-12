from typing import Any, Dict, Optional, TypeVar, Generic, List, TypedDict
from pydantic import BaseModel, Field
from datetime import datetime
import json
from enum import Enum

from config.common import LocationInfo


class IpStackResponse(BaseModel):
    """Response model for IP Stack API."""
    ip: str
    continent_name: Optional[str]
    country_name: Optional[str]
    country_code: Optional[str]
    region_name: Optional[str]
    city: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    type: Optional[str]  # ipv4 or ipv6


class CallerName(BaseModel):
    """Caller name information from Twilio Lookup."""
    caller_name: Optional[str]
    caller_type: Optional[str]
    error_code: Optional[int]


class CarrierInfo(BaseModel):
    """Carrier information from Twilio Lookup."""
    mobile_country_code: Optional[str]
    mobile_network_code: Optional[str]
    name: Optional[str]
    type: Optional[str]
    error_code: Optional[int]


class TwilioLookupResponse(BaseModel):
    """Response model for Twilio Lookup API."""
    caller_name: Optional[CallerName]
    country_code: Optional[str]
    phone_number: str
    national_format: Optional[str]
    carrier: Optional[CarrierInfo]
    add_ons: Optional[Dict[str, Any]]
    url: Optional[str]


class OSInfo(BaseModel):
    """Operating system information from UserStack."""
    name: Optional[str]
    code: Optional[str]
    url: Optional[str]
    family: Optional[str]
    family_code: Optional[str]
    family_vendor: Optional[str]
    icon: Optional[str]
    icon_large: Optional[str]


class DeviceInfo(BaseModel):
    """Device information from UserStack."""
    is_mobile_device: Optional[bool]
    type: Optional[str]
    brand: Optional[str]
    brand_code: Optional[str]
    brand_url: Optional[str]
    name: Optional[str]


class BrowserInfo(BaseModel):
    """Browser information from UserStack."""
    name: Optional[str]
    version: Optional[str]
    version_major: Optional[str]
    engine: Optional[str]


class CrawlerInfo(BaseModel):
    """Crawler information from UserStack."""
    is_crawler: Optional[bool]
    category: Optional[str]
    last_seen: Optional[str]


class UserStackResponse(BaseModel):
    """Response model for UserStack API."""
    ua: str
    type: Optional[str]
    brand: Optional[str]
    name: Optional[str]
    url: Optional[str]
    os: Optional[OSInfo]
    device: Optional[DeviceInfo]
    browser: Optional[BrowserInfo]
    crawler: Optional[CrawlerInfo]


class SecurityInfo(BaseModel):
    """Security information from VPN API."""
    vpn: bool = False
    proxy: bool = False
    tor: bool = False
    relay: bool = False


class CurrencyInfo(BaseModel):
    """Currency information from IP Geolocation API."""
    code: Optional[str]
    name: Optional[str]
    symbol: Optional[str]


class DSTInfo(BaseModel):
    """Daylight Saving Time information from IP Geolocation API."""
    utc_time: Optional[str]
    duration: Optional[str]
    gap: Optional[bool]
    dateTimeAfter: Optional[str]
    dateTimeBefore: Optional[str]
    overlap: Optional[bool]


class TimeZoneInfo(BaseModel):
    """Time zone information from IP Geolocation API."""
    name: Optional[str]
    offset: Optional[int]
    offset_with_dst: Optional[int]
    current_time: Optional[str]
    current_time_unix: Optional[float]
    is_dst: Optional[bool]
    dst_savings: Optional[int]
    dst_exists: Optional[bool]
    dst_start: Optional[DSTInfo]
    dst_end: Optional[DSTInfo]


class IPGeolocationResponse(BaseModel):
    """Response model for IP Geolocation API."""
    ip: str
    continent_code: Optional[str]
    continent_name: Optional[str]
    country_code2: Optional[str]
    country_code3: Optional[str]
    country_name: Optional[str]
    country_name_official: Optional[str]
    country_capital: Optional[str]
    state_prov: Optional[str]
    state_code: Optional[str]
    district: Optional[str]
    city: Optional[str]
    zipcode: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]
    is_eu: Optional[bool]
    calling_code: Optional[str]
    country_tld: Optional[str]
    languages: Optional[str]
    country_flag: Optional[str]
    country_emoji: Optional[str]
    geoname_id: Optional[str]
    isp: Optional[str]
    connection_type: Optional[str]
    organization: Optional[str]
    currency: Optional[CurrencyInfo]
    time_zone: Optional[TimeZoneInfo]
    security: Optional[SecurityInfo] = None


class VpnApiResponse(BaseModel):
    """Response model for VPN API."""
    ip: str
    security: SecurityInfo = Field(default_factory=SecurityInfo)


SelectType = TypeVar('SelectType', bound=BaseModel|str)
InfoType = TypeVar('InfoType', bound=BaseModel|None|datetime)


def optional_factory() -> Optional[Any]:
    return None


class GenericBaseModel(BaseModel, Generic[SelectType, InfoType]):
    server: Optional[SelectType] = Field(default_factory=optional_factory)
    header: Optional[SelectType] = Field(default_factory=optional_factory)
    selected: Optional[SelectType] = None
    source: Optional[str] = None
    info: Optional[InfoType] = None

    def to_json(self) -> str:
        return json.dumps(self.model_dump(), sort_keys=True, ensure_ascii=True, indent=2)


class WarningStatus(BaseModel):
    """Base model for warning status."""
    status: str
    message: str
    category: Optional[str] = None


class IpChecks(BaseModel):
    """Model for IP security checks."""
    vpn: Optional[WarningStatus] = None
    proxy: Optional[WarningStatus] = None
    tor: Optional[WarningStatus] = None
    relay: Optional[WarningStatus] = None


class IpData(GenericBaseModel[IPGeolocationResponse, None]):
    def getTimezone(self) -> Optional[str]:
        return self.info.time_zone.name if self.info and self.info.time_zone else None
    
    def getLocation(self) -> Optional[LocationInfo]:
        if self.info and self.info.latitude and self.info.longitude:
            return LocationInfo(latitude=float(self.info.latitude), longitude=float(self.info.longitude))
        return None

    def getLatitude(self) -> Optional[float]:
        location: Optional[LocationInfo] = self.getLocation()
        return location.latitude if location else None

    def getLongitude(self) -> Optional[float]:
        location: Optional[LocationInfo] = self.getLocation()
        return location.longitude if location else None
    
    def isHeaderVpn(self) -> bool:
        if self.header and self.header.security:
            return self.header.security.vpn
        return False
        
    def isHeaderTor(self) -> bool:
        if self.header and self.header.security:
            return self.header.security.tor
        return False
    
    def isHeaderProxy(self) -> bool:
        if self.header and self.header.security:
            return self.header.security.proxy
        return False
    
    def isHeaderRelay(self) -> bool:
        if self.header and self.header.security:
            return self.header.security.relay
        return False
    
    def isServerVpn(self) -> bool:
        if self.server and self.server.security:
            return self.server.security.vpn
        return False
        
    def isServerTor(self) -> bool:
        if self.server and self.server.security:
            return self.server.security.tor
        return False
    
    def isServerProxy(self) -> bool:
        if self.server and self.server.security:
            return self.server.security.proxy
        return False
    
    def isServerRelay(self) -> bool:
        if self.server and self.server.security:
            return self.server.security.relay
        return False
    
    def getLocales(self) -> Optional[List[str]]:
        if self.info and self.info.languages:
            return self.info.languages.split(',')
        return None
    
    def getHeaderIpAddress(self) -> Optional[str]:
        if self.header and self.header.ip:
            return self.header.ip
        return None
    
    def getServerIpAddress(self) -> Optional[str]:
        if self.server and self.server.ip:
            return self.server.ip
        return None
    
    def getSelectedAddress(self) -> Optional[str]:
        if self.selected:
            return self.selected.ip
        return None
    
    def getSelectedCountry(self) -> Optional[str]:
        if self.info and self.info.country_code2:
            return self.info.country_code2
        return None

    def getSelectedCountryName(self) -> Optional[str]:
        if self.selected and self.selected.country_name:
            return self.selected.country_name
        return None

    def getSelectedRegion(self) -> Optional[str]:
        if self.selected and self.selected.state_prov:
            return self.selected.state_prov
        return None

    def getSelectedCity(self) -> Optional[str]:
        if self.selected and self.selected.city:
            return self.selected.city
        return None

    def getSelectedOrganization(self) -> Optional[str]:
        if self.selected and self.selected.organization:
            return self.selected.organization
        return None

    def getSelectedISP(self) -> Optional[str]:
        if self.selected and self.selected.isp:
            return self.selected.isp
        return None

    def get_security_checks(self) -> List[WarningStatus]:
        """Check for VPN, proxy, Tor and Relay usage in server and header."""
        
        checks: List[WarningStatus] = []
        
        if self.server and self.server.security:
            checks.extend([
                WarningStatus(
                    status='warning' if self.isServerVpn() else 'success',
                    category='vpn',
                    message='⚠️ VPN usage detected in server' if self.isServerVpn() else '✅ No VPN detected in server'
                ),
                WarningStatus(
                    status='warning' if self.isServerProxy() else 'success',
                    category='proxy',
                    message='⚠️ Proxy usage detected in server' if self.isServerProxy() else '✅ No proxy detected in server'
                ),
                WarningStatus(
                    status='warning' if self.isServerTor() else 'success',
                    category='tor',
                    message='⚠️ Tor usage detected in server' if self.isServerTor() else '✅ No Tor detected in server'
                ),
                WarningStatus(
                    status='warning' if self.isServerRelay() else 'success',
                    category='relay',
                    message='⚠️ Relay usage detected in server' if self.isServerRelay() else '✅ No Relay detected in server'
                )
            ])
        else:
            checks.append(WarningStatus(
                status='warning',
                category='security',
                message='⚠️ Could not perform security checks for server'
            ))

        if self.header and self.header.security:
            checks.extend([
                WarningStatus(
                    status='warning' if self.isHeaderVpn() else 'success',
                    category='vpn',
                    message='⚠️ VPN usage detected in header' if self.isHeaderVpn() else '✅ No VPN detected in header'
                ),
                WarningStatus(
                    status='warning' if self.isHeaderProxy() else 'success',
                    category='proxy',
                    message='⚠️ Proxy usage detected in header' if self.isHeaderProxy() else '✅ No proxy detected in header'
                ),
                WarningStatus(
                    status='warning' if self.isHeaderTor() else 'success',
                    category='tor',
                    message='⚠️ Tor usage detected in header' if self.isHeaderTor() else '✅ No Tor detected in header'
                ),
                WarningStatus(
                    status='warning' if self.isHeaderRelay() else 'success',
                    category='relay',
                    message='⚠️ Relay usage detected in header' if self.isHeaderRelay() else '✅ No Relay detected in header'
                )
            ])
        else:
            checks.append(WarningStatus(
                status='warning',
                category='security',
                message='⚠️ Could not perform security checks for header'
            ))

        return checks

    def get_ip_mismatch(self) -> WarningStatus:
        """Check for IP address mismatches between server and client."""
        server_ip = self.server.ip if self.server and self.server.ip else None
        header_ip = self.header.ip if self.header and self.header.ip else None
        header_ip_changed = server_ip != header_ip
        
        return WarningStatus(
            status='warning' if header_ip_changed else 'success',
            message='⚠️ IP Address Mismatch: Server IP differs from Header IP' if header_ip_changed else '✅ IP addresses match'
        )

    def get_country_mismatch(self) -> WarningStatus:
        """Check for country mismatches between server and client."""
        server_country = self.server.country_code2 if self.server and self.server.country_code2 else None
        header_country = self.header.country_code2 if self.header and self.header.country_code2 else None
        country_mismatch = server_country != header_country
        
        return WarningStatus(
            status='warning' if country_mismatch else 'success',
            message='⚠️ Country Mismatch: Server country differs from Header country' if country_mismatch else '✅ Countries match'
        )

    def get_timezone_mismatch(self) -> WarningStatus:
        """Check for timezone mismatches."""
        server_timezone = self.server.time_zone.name if self.server and self.server.time_zone else None
        header_timezone = self.header.time_zone.name if self.header and self.header.time_zone else None
        timezone_mismatch = server_timezone != header_timezone
        
        return WarningStatus(
            status='warning' if timezone_mismatch else 'success',
            message='⚠️ Timezone Mismatch: Header timezone differs from IP timezone' if timezone_mismatch else '✅ Timezones match'
        )

    def get_locale_mismatch(self) -> WarningStatus:
        """Check for locale mismatches between server and client."""
        server_locale = self.server.languages.split(',')[0] if self.server and self.server.languages else None
        header_locale = self.header.languages.split(',')[0] if self.header and self.header.languages else None
        locale_mismatch = server_locale != header_locale
        
        return WarningStatus(
            status='warning' if locale_mismatch else 'success',
            message='⚠️ Locale Mismatch: Server locale differs from Browser locale' if locale_mismatch else '✅ Locales match'
        )


class UserAgentData(GenericBaseModel[str, UserStackResponse]):
    def get_os_name(self) -> Optional[str]:
        return self.info.os.name if self.info and self.info.os else None

    def get_browser_name(self) -> Optional[str]:
        return self.info.browser.name if self.info and self.info.browser else None
    
    def is_crawler(self) -> Optional[bool]:
        return self.info.crawler.is_crawler if self.info and self.info.crawler else None

    def get_platform_type(self) -> Optional[str]:
        return self.info.device.type if self.info and self.info.device else None

    def has_user_agent_mismatch(self) -> bool:
        return self.server != self.header

    def get_user_agent_mismatch(self) -> WarningStatus:
        """Check for user agent mismatches."""
        return WarningStatus(
            status='warning' if self.has_user_agent_mismatch() else 'success',
            message='⚠️ User Agent Mismatch: Server and Client user agents differ' if self.has_user_agent_mismatch() else '✅ User agents match'
        )

    def get_crawler_detection(self) -> WarningStatus:
        """Check for crawler/bot detection."""
        return WarningStatus(
            status='warning' if self.is_crawler() else 'success',
            message='⚠️ Crawler/Bot Detected' if self.is_crawler() else '✅ No crawler detected'
        )


class LocaleData(GenericBaseModel[str, None]):
    pass


class LocationData(GenericBaseModel[LocationInfo, None]):

    def getLatitude(self) -> Optional[float]:
        if self.selected and self.selected.latitude:
            return float(self.selected.latitude)
        else:
            return None

    def getLongitude(self) -> Optional[float]:
        if self.selected and self.selected.longitude:
            return float(self.selected.longitude)
        else:
            return None

# Time Data
class TimeData(GenericBaseModel[str, datetime]):

    def getTimezone(self) -> Optional[str]:
        return self.selected if self.selected else None


class PublishingType(str, Enum):
    """Types of publishing methods."""
    WEBSITE = 'website'
    SOCIAL_MEDIA = 'social_media'
    EMAIL = 'email'
    SMS = 'sms'
    DIRECT_MAIL = 'direct_mail'

    @classmethod
    def choices(cls) -> List[tuple[str, str]]:
        return [(choice.value, choice.value.replace('_', ' ').title()) for choice in cls]

class TrackingType(str, Enum):
    """Types of tracking methods."""
    GPS = 'gps'
    IP = 'ip'
    BROWSER = 'browser'
    USER_AGENT = 'user_agent'
    COOKIES = 'cookies'

    @classmethod
    def choices(cls) -> List[tuple[str, str]]:
        return [(choice.value, choice.value.replace('_', ' ').title()) for choice in cls]

class TrackingData(TypedDict):
    """Type for tracking data."""
    server_timestamp: str
    http_method: str
    ip_address: str
    ip_source: str
    os: str
    browser: str
    platform: str
    locale: str
    client_time: str
    client_timezone: str
    latitude: Optional[float]
    longitude: Optional[float]
    location_source: str
    ip_data: Dict[str, Any]
    user_agent_data: Dict[str, Any]
    header_data: Dict[str, Any]
    form_data: Dict[str, Any]
