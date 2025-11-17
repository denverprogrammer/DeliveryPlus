import json

from datetime import datetime
from datetime import UTC
from typing import Any
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import TypedDict
from typing import TypeVar
from django.http import HttpRequest
from ipware import get_client_ip
from pydantic import BaseModel
from pydantic import Field


class IpAddressInfo(BaseModel):
    address: str = ""
    is_routable: bool = False


# Location Data
class LocationInfo(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# Header Data
class NavigatorInfo(BaseModel):
    connection: str = Field(default="unknown")
    language: str = Field(default="unknown")
    user_agent: str = Field(default="unknown")


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
    connection_type: str = Field(default="unknown")


class HeaderData(BaseModel):
    navigator: NavigatorInfo = Field(default_factory=NavigatorInfo)
    datetime: DateTimeInfo
    public_ip: HeaderIpInfo

    def to_json(self) -> str:
        return json.dumps(self.model_dump(), sort_keys=True, ensure_ascii=True, indent=2)

    def getLocation(self) -> Optional[LocationInfo]:
        if self.public_ip and self.public_ip.location:
            return self.public_ip.location
        return None

    def getLatitude(self) -> Optional[float]:
        if self.public_ip and self.public_ip.location and self.public_ip.location.latitude:
            try:
                return float(self.public_ip.location.latitude)
            except (ValueError, TypeError):
                return None
        return None

    def getLongitude(self) -> Optional[float]:
        if self.public_ip and self.public_ip.location and self.public_ip.location.longitude:
            return float(self.public_ip.location.longitude)
        return None

    def getTimezone(self) -> Optional[str]:
        return self.datetime.timezone if self.datetime else None

    def getLocale(self) -> Optional[str]:
        return self.navigator.language if self.navigator else None

    def getHeaderCountry(self) -> Optional[str]:
        return self.public_ip.address.country if self.public_ip and self.public_ip.address else None

    def getTimestamp(self) -> int:
        if self.datetime.timestamp:
            return int(self.datetime.timestamp)
        return int(datetime.now(UTC).timestamp() * 1000)

    def getHeaderIpAddress(self) -> Optional[IpAddressInfo]:
        if self.public_ip and self.public_ip.ip:
            return IpAddressInfo(address=self.public_ip.ip, is_routable=True)
        return None

    def getClientIpAddress(self, request: HttpRequest) -> Optional[IpAddressInfo]:
        server_ip, is_routable = get_client_ip(request)
        if self.public_ip and self.public_ip.ip:
            return IpAddressInfo(address=server_ip, is_routable=is_routable)
        return None


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

    caller_name: Optional[str] = None
    caller_type: Optional[str] = None
    error_code: Optional[int] = None


class CarrierInfo(BaseModel):
    """Carrier information from Twilio Lookup."""

    mobile_country_code: Optional[str] = None
    mobile_network_code: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    error_code: Optional[int] = None


class TwilioLookupResponse(BaseModel):
    """Response model for Twilio Lookup API."""

    caller_name: Optional[CallerName] = None
    country_code: Optional[str] = None
    phone_number: str
    national_format: Optional[str] = None
    carrier: Optional[CarrierInfo] = None
    add_ons: Optional[Dict[str, Any]] = None
    url: Optional[str] = None


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


class PostGridDetails(BaseModel):
    """Detailed address information from PostGrid API."""

    street_name: Optional[str] = Field(None, alias="streetName")
    street_direction: Optional[str] = Field(None, alias="streetDirection")
    box_id: Optional[str] = Field(None, alias="boxID")
    delivery_installation_area_name: Optional[str] = Field(
        None, alias="deliveryInstallationAreaName"
    )
    delivery_installation_type: Optional[str] = Field(None, alias="deliveryInstallationType")
    delivery_installation_qualifier: Optional[str] = Field(
        None, alias="deliveryInstallationQualifier"
    )
    rural_route_number: Optional[str] = Field(None, alias="ruralRouteNumber")
    rural_route_type: Optional[str] = Field(None, alias="ruralRouteType")
    extra_info: Optional[str] = Field(None, alias="extraInfo")
    street_type: Optional[str] = Field(None, alias="streetType")
    street_number: Optional[str] = Field(None, alias="streetNumber")
    suite_id: Optional[str] = Field(None, alias="suiteID")
    county: Optional[str] = None
    county_num: Optional[str] = Field(None, alias="countyNum")
    us_census_cmsa: Optional[str] = Field(None, alias="usCensusCMSA")
    us_census_block_number: Optional[str] = Field(None, alias="usCensusBlockNumber")
    us_census_tract_number: Optional[str] = Field(None, alias="usCensusTractNumber")
    us_census_ma: Optional[str] = Field(None, alias="usCensusMA")
    us_census_msa: Optional[str] = Field(None, alias="usCensusMSA")
    us_census_pmsa: Optional[str] = Field(None, alias="usCensusPMSA")
    us_has_daylight_savings: Optional[bool] = Field(None, alias="usHasDaylightSavings")
    us_time_zone: Optional[str] = Field(None, alias="usTimeZone")
    us_congressional_district_number: Optional[str] = Field(
        None, alias="usCongressionalDistrictNumber"
    )
    us_state_legislative_lower: Optional[str] = Field(None, alias="usStateLegislativeLower")
    us_state_legislative_upper: Optional[str] = Field(None, alias="usStateLegislativeUpper")
    us_mailings_carrier_route: Optional[str] = Field(None, alias="usMailingsCarrierRoute")
    us_mailings_default_flag: Optional[bool] = Field(None, alias="usMailingsDefaultFlag")
    us_mailings_delivery_point: Optional[str] = Field(None, alias="usMailingsDeliveryPoint")
    us_mailings_dpv_confirmation_indicator: Optional[str] = Field(
        None, alias="usMailingsDpvConfirmationIndicator"
    )
    us_mailings_dpv_crma_indicator: Optional[str] = Field(None, alias="usMailingsDpvCrmaIndicator")
    us_mailings_dpv_footnote1: Optional[str] = Field(None, alias="usMailingsDpvFootnote1")
    us_mailings_dpv_footnote2: Optional[str] = Field(None, alias="usMailingsDpvFootnote2")
    us_mailings_elot_asc_desc: Optional[str] = Field(None, alias="usMailingsElotAscDesc")
    us_mailings_elot_sequence_number: Optional[str] = Field(
        None, alias="usMailingsElotSequenceNumber"
    )
    us_mailings_ews_flag: Optional[str] = Field(None, alias="usMailingsEWSFlag")
    us_mailings_record_type_code: Optional[str] = Field(None, alias="usMailingsRecordTypeCode")
    residential: Optional[bool] = None
    vacant: Optional[bool] = None
    us_mailings_lacs_flag: Optional[str] = Field(None, alias="usMailingsLACSFlag")
    us_mailing_check_digit: Optional[str] = Field(None, alias="usMailingCheckDigit")
    us_mailings_dpv_footnote3: Optional[str] = Field(None, alias="usMailingsDpvFootnote3")
    us_mailings_lacs_return_code: Optional[str] = Field(None, alias="usMailingsLACSReturnCode")
    us_mailings_suite_link_return_code: Optional[str] = Field(
        None, alias="usMailingsSuiteLinkReturnCode"
    )
    suite_key: Optional[str] = Field(None, alias="suiteKey")
    us_area_code: Optional[str] = Field(None, alias="usAreaCode")
    pre_direction: Optional[str] = Field(None, alias="preDirection")
    post_direction: Optional[str] = Field(None, alias="postDirection")
    us_census_fips: Optional[str] = Field(None, alias="usCensusFIPS")
    us_postnet_barcode: Optional[str] = Field(None, alias="usPostnetBarcode")
    us_mailings_lacs_indicator: Optional[str] = Field(None, alias="usMailingsLACSIndicator")
    us_intelligent_mail_barcode_key: Optional[str] = Field(
        None, alias="usIntelligentMailBarcodeKey"
    )

    class Config:
        populate_by_name = True


class PostGridVerificationData(BaseModel):
    """Verification data from PostGrid API."""

    city: Optional[str] = None
    country: Optional[str] = None
    details: Optional[PostGridDetails] = None
    errors: Optional[Dict[str, List[str]]] = None
    line1: Optional[str] = None
    line2: Optional[str] = None
    postal_or_zip: Optional[str] = Field(None, alias="postalOrZip")
    province_or_state: Optional[str] = Field(None, alias="provinceOrState")
    status: Optional[str] = None  # e.g., "corrected", "verified", etc.
    recipient: Optional[str] = None

    class Config:
        populate_by_name = True


class PostGridApiResponse(BaseModel):
    """Response model for PostGrid Address Verification API."""

    status: str  # e.g., "success", "error"
    message: Optional[str] = None
    data: Optional[PostGridVerificationData] = None


SelectType = TypeVar("SelectType", bound=BaseModel | str)
InfoType = TypeVar("InfoType", bound=BaseModel | None | datetime)


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
        if self.selected and self.selected.time_zone:
            return self.selected.time_zone.name
        return None

    def getLocation(self) -> Optional[LocationInfo]:
        if self.selected and self.selected.latitude and self.selected.longitude:
            return LocationInfo(
                latitude=float(self.selected.latitude),
                longitude=float(self.selected.longitude),
            )
        return None

    def getLatitude(self) -> Optional[float]:
        location = self.getLocation()
        return location.latitude if location else None

    def getLongitude(self) -> Optional[float]:
        location = self.getLocation()
        return location.longitude if location else None

    def isHeaderVpn(self) -> bool:
        return bool(self.header and self.header.security and self.header.security.vpn)

    def isHeaderTor(self) -> bool:
        return bool(self.header and self.header.security and self.header.security.tor)

    def isHeaderProxy(self) -> bool:
        return bool(self.header and self.header.security and self.header.security.proxy)

    def isHeaderRelay(self) -> bool:
        return bool(self.header and self.header.security and self.header.security.relay)

    def isServerVpn(self) -> bool:
        return bool(self.server and self.server.security and self.server.security.vpn)

    def isServerTor(self) -> bool:
        return bool(self.server and self.server.security and self.server.security.tor)

    def isServerProxy(self) -> bool:
        return bool(self.server and self.server.security and self.server.security.proxy)

    def isServerRelay(self) -> bool:
        return bool(self.server and self.server.security and self.server.security.relay)

    def getLocales(self) -> Optional[List[str]]:
        if self.selected and self.selected.languages:
            return [lang.strip() for lang in self.selected.languages.split(",")]
        return None

    def getHeaderIpAddress(self) -> Optional[str]:
        return self.header.ip if self.header else None

    def getServerIpAddress(self) -> Optional[str]:
        return self.server.ip if self.server else None

    def getSelectedAddress(self) -> Optional[str]:
        return self.selected.ip if self.selected else None

    def getSelectedCountry(self) -> Optional[str]:
        return self.selected.country_code2 if self.selected else None

    def getSelectedCountryName(self) -> Optional[str]:
        return self.selected.country_name if self.selected else None

    def getSelectedRegion(self) -> Optional[str]:
        return self.selected.state_prov if self.selected else None

    def getSelectedCity(self) -> Optional[str]:
        return self.selected.city if self.selected else None

    def getSelectedOrganization(self) -> Optional[str]:
        return self.selected.organization if self.selected else None

    def getSelectedISP(self) -> Optional[str]:
        return self.selected.isp if self.selected else None

    def get_security_checks(self) -> List[WarningStatus]:
        checks = []
        if self.isHeaderVpn() or self.isServerVpn():
            checks.append(
                WarningStatus(
                    status="warning",
                    message="VPN detected",
                    category="security",
                )
            )
        if self.isHeaderTor() or self.isServerTor():
            checks.append(
                WarningStatus(
                    status="warning",
                    message="Tor detected",
                    category="security",
                )
            )
        if self.isHeaderProxy() or self.isServerProxy():
            checks.append(
                WarningStatus(
                    status="warning",
                    message="Proxy detected",
                    category="security",
                )
            )
        if self.isHeaderRelay() or self.isServerRelay():
            checks.append(
                WarningStatus(
                    status="warning",
                    message="Relay detected",
                    category="security",
                )
            )
        return checks

    def get_ip_mismatch(self) -> WarningStatus:
        header_ip = self.getHeaderIpAddress()
        server_ip = self.getServerIpAddress()
        selected_ip = self.getSelectedAddress()

        if header_ip and server_ip and header_ip != server_ip:
            return WarningStatus(
                status="warning",
                message=f"IP mismatch: Header IP ({header_ip}) != Server IP ({server_ip})",
                category="ip",
            )
        if selected_ip and server_ip and selected_ip != server_ip:
            return WarningStatus(
                status="warning",
                message=f"IP mismatch: Selected IP ({selected_ip}) != Server IP ({server_ip})",
                category="ip",
            )
        return WarningStatus(
            status="success",
            message="No IP mismatch detected",
            category="ip",
        )

    def get_country_mismatch(self) -> WarningStatus:
        header_country = self.header.country_code2 if self.header else None
        server_country = self.server.country_code2 if self.server else None
        selected_country = self.selected.country_code2 if self.selected else None

        if header_country and server_country and header_country != server_country:
            return WarningStatus(
                status="warning",
                message=f"Country mismatch: Header country ({header_country}) != Server country ({server_country})",
                category="country",
            )
        if selected_country and server_country and selected_country != server_country:
            return WarningStatus(
                status="warning",
                message=f"Country mismatch: Selected country ({selected_country}) != Server country ({server_country})",
                category="country",
            )
        return WarningStatus(
            status="success",
            message="No country mismatch detected",
            category="country",
        )

    def get_timezone_mismatch(self) -> WarningStatus:
        header_timezone = (
            self.header.time_zone.name if self.header and self.header.time_zone else None
        )
        server_timezone = (
            self.server.time_zone.name if self.server and self.server.time_zone else None
        )
        selected_timezone = (
            self.selected.time_zone.name if self.selected and self.selected.time_zone else None
        )

        if header_timezone and server_timezone and header_timezone != server_timezone:
            return WarningStatus(
                status="warning",
                message=f"Timezone mismatch: Header timezone ({header_timezone}) != Server timezone ({server_timezone})",
                category="timezone",
            )
        if selected_timezone and server_timezone and selected_timezone != server_timezone:
            return WarningStatus(
                status="warning",
                message=f"Timezone mismatch: Selected timezone ({selected_timezone}) != Server timezone ({server_timezone})",
                category="timezone",
            )
        return WarningStatus(
            status="success",
            message="No timezone mismatch detected",
            category="timezone",
        )

    def get_locale_mismatch(self) -> WarningStatus:
        header_locales = self.getLocales() if self.header else None
        server_locales = self.getLocales() if self.server else None
        selected_locales = self.getLocales() if self.selected else None

        if header_locales and server_locales and set(header_locales) != set(server_locales):
            return WarningStatus(
                status="warning",
                message=f"Locale mismatch: Header locales ({header_locales}) != Server locales ({server_locales})",
                category="locale",
            )
        if selected_locales and server_locales and set(selected_locales) != set(server_locales):
            return WarningStatus(
                status="warning",
                message=f"Locale mismatch: Selected locales ({selected_locales}) != Server locales ({server_locales})",
                category="locale",
            )
        return WarningStatus(
            status="success",
            message="No locale mismatch detected",
            category="locale",
        )


class UserAgentData(GenericBaseModel[str, UserStackResponse]):
    def get_os_name(self) -> Optional[str]:
        return self.info.os.name if self.info and self.info.os else None

    def get_browser_name(self) -> Optional[str]:
        return self.info.browser.name if self.info and self.info.browser else None

    def is_crawler(self) -> Optional[bool]:
        return self.info.crawler.is_crawler if self.info and self.info.crawler else None

    def get_platform_type(self) -> Optional[str]:
        return self.info.type if self.info else None

    def has_user_agent_mismatch(self) -> bool:
        return bool(self.server and self.header and self.server != self.header)

    def get_user_agent_mismatch(self) -> WarningStatus:
        if self.has_user_agent_mismatch():
            return WarningStatus(
                status="warning",
                message=f"User agent mismatch: Header UA ({self.header}) != Server UA ({self.server})",
                category="user_agent",
            )
        return WarningStatus(
            status="success",
            message="No user agent mismatch detected",
            category="user_agent",
        )

    def get_crawler_detection(self) -> WarningStatus:
        if self.is_crawler():
            return WarningStatus(
                status="warning",
                message="Crawler detected",
                category="crawler",
            )
        return WarningStatus(
            status="success",
            message="No crawler detected",
            category="crawler",
        )


class LocaleData(GenericBaseModel[str, None]):
    pass


class LocationData(GenericBaseModel[LocationInfo, None]):
    def getLatitude(self) -> Optional[float]:
        return self.selected.latitude if self.selected else None

    def getLongitude(self) -> Optional[float]:
        return self.selected.longitude if self.selected else None


class TimeData(GenericBaseModel[str, datetime]):
    def getTimezone(self) -> Optional[str]:
        return self.selected if self.selected else None


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
