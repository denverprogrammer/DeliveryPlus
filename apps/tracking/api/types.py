from typing import Any, Dict, Optional, TypeVar, Generic
from pydantic import BaseModel, Field
from datetime import datetime
import json
from config.common import IpAddressInfo, LocationInfo


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
    hosting: bool = False


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
        return json.dumps(self.model_dump(), sort_keys=True, ensure_ascii=True)


class IpData(GenericBaseModel[IpAddressInfo, IPGeolocationResponse]):

    def getTimezone(self) -> Optional[str]:
        return self.info.time_zone.name if self.info and self.info.time_zone else None

    def to_json(self) -> str:
        return json.dumps(self.model_dump(), sort_keys=True, ensure_ascii=True)
    
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
    
    def getSelectedAddress(self) -> Optional[str]:
        if self.selected:
            return self.selected.address
        return None


class UserAgentData(GenericBaseModel[str, UserStackResponse]):
    def get_os_name(self) -> Optional[str]:
        return self.info.os.name if self.info and self.info.os else None

    def get_browser_name(self) -> Optional[str]:
        return self.info.browser.name if self.info and self.info.browser else None

    def get_platform_type(self) -> Optional[str]:
        return self.info.device.type if self.info and self.info.device else None

    def has_user_agent_mismatch(self) -> bool:
        return self.server != self.header

    def to_json(self) -> str:
        return json.dumps(self.model_dump(), sort_keys=True, ensure_ascii=True)


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
