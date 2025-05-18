import json
from typing import Optional
from django.http import HttpRequest
from pydantic import BaseModel, Field
from datetime import datetime, UTC
from ipware import get_client_ip


class IpAddressInfo(BaseModel):
    address: str = ''
    is_routable: bool = False


# Location Data
class LocationInfo(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


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
