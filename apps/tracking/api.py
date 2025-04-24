from datetime import timedelta
from pydantic import BaseModel, Field
import requests
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import pprint
import redis
import json
from datetime import timedelta
from pydantic import BaseModel
from typing import Optional, Dict

from typing import Optional, Any
import json
import redis
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional, Any


from pydantic import BaseModel
from typing import Optional


class BaseApiClient(ABC):
    def __init__(self, redis_db: int, redis_prefix: str):
        self.redis_client = redis.Redis(host='redis', port=6379, db=redis_db, decode_responses=True)
        self.redis_prefix = redis_prefix

    def get_cache_key(self, identifier: str) -> str:
        return f'{self.redis_prefix}:{identifier}'

    def get_cache_data(self, identifier: str) -> Optional[dict[str, Any]]:
        value = self.redis_client.get(self.get_cache_key(identifier))
        return json.loads(value) if value else None

    def put_cache_data(self, identifier: str, data: dict[str, Any], ttl_seconds: int = 3600) -> bool:
        return self.redis_client.setex(
            self.get_cache_key(identifier),
            timedelta(seconds=ttl_seconds),
            json.dumps(data)
        )

    @abstractmethod
    def get_data(self, identifier: str) -> Optional[dict[str, Any]]:
        pass


######################
#  IP Stack models  ##
######################

class IpStackResponse(BaseModel):
    ip: str
    continent_name: Optional[str]
    country_name: Optional[str]
    country_code: Optional[str]
    region_name: Optional[str]
    city: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    type: Optional[str]  # ipv4 or ipv6

class IpStackApiClient(BaseApiClient):
    BASE_URL = 'http://api.ipstack.com/'

    def __init__(self, api_key: str):
        super().__init__(redis_db=1, redis_prefix='ip_address')
        self.api_key = api_key

    def get_data(self, identifier: str) -> Optional[dict[str, Any]]:
        try:
            cache_data = self.get_cache_data(identifier)
            if cache_data:
                return cache_data

            response = requests.get(
                f'{self.BASE_URL}{identifier}',
                params={'access_key': self.api_key},
                timeout=5
            )
            response.raise_for_status()

            response_data = response.json()
            self.put_cache_data(identifier, response_data)

            return response_data

        except requests.RequestException as e:
            print(f'Error querying IpStack API: {e}')
            return None
        except Exception as e:
            print(f'Error parsing IpStack API response: {e}')
            return None


##########################
#  TwilioLookup models  ##
##########################

class CallerName(BaseModel):
    caller_name: Optional[str]
    caller_type: Optional[str]
    error_code: Optional[int]

class CarrierInfo(BaseModel):
    mobile_country_code: Optional[str]
    mobile_network_code: Optional[str]
    name: Optional[str]
    type: Optional[str]
    error_code: Optional[int]

class TwilioLookupResponse(BaseModel):
    caller_name: Optional[CallerName]
    country_code: Optional[str]
    phone_number: str
    national_format: Optional[str]
    carrier: Optional[CarrierInfo]
    add_ons: Optional[Dict[str, Any]]
    url: Optional[str]

class TwilioApiClient(BaseApiClient):
    def __init__(self, account_sid: str, auth_token: str):
        super().__init__(redis_db=2, redis_prefix='phone_number')
        self.client = Client(account_sid, auth_token)

    def get_data(self, identifier: str) -> Optional[dict[str, Any]]:
        try:
            cache_data = self.get_cache_data(identifier)
            if cache_data:
                return cache_data

            response = self.client.lookups.v2.phone_numbers(identifier).fetch(fields=[
                'caller_name',
                'sim_swap',
                'call_forwarding',
                'line_status',
                'line_type_intelligence',
                'identity_match',
                'reassigned_number',
                'sms_pumping_risk',
                'phone_number_quality_score',
                'pre_fill'
            ])

            response_data = response.__dict__
            response_data.pop('_version', None)
            response_data.pop('url', None)
            self.put_cache_data(identifier, response_data)

            return response_data

        except TwilioRestException as e:
            if e.code == 20404:
                return None
            print(f'Error querying Twilio Lookup API: {e}')
            raise e


#######################
#  UserStack models  ##
#######################

class OSInfo(BaseModel):
    name: Optional[str]
    code: Optional[str]
    url: Optional[str]
    family: Optional[str]
    family_code: Optional[str]
    family_vendor: Optional[str]
    icon: Optional[str]
    icon_large: Optional[str]

class DeviceInfo(BaseModel):
    is_mobile_device: Optional[bool]
    type: Optional[str]
    brand: Optional[str]
    brand_code: Optional[str]
    brand_url: Optional[str]
    name: Optional[str]

class BrowserInfo(BaseModel):
    name: Optional[str]
    version: Optional[str]
    version_major: Optional[str]
    engine: Optional[str]

class CrawlerInfo(BaseModel):
    is_crawler: Optional[bool]
    category: Optional[str]
    last_seen: Optional[str]

class UserStackResponse(BaseModel):
    ua: str
    type: Optional[str]
    brand: Optional[str]
    name: Optional[str]
    url: Optional[str]
    os: Optional[OSInfo]
    device: Optional[DeviceInfo]
    browser: Optional[BrowserInfo]
    crawler: Optional[CrawlerInfo]

class UserStackApiClient(BaseApiClient):
    BASE_URL = 'http://api.userstack.com/detect'

    def __init__(self, api_key: str):
        # Use separate Redis DB for user-agent cache
        super().__init__(redis_db=3, redis_prefix='user_agent')
        self.api_key = api_key

    def get_data(self, identifier: str) -> Optional[UserStackResponse]:
        try:
            # Step 1: Check cache first
            cache_data = self.get_cache_data(identifier)
            if cache_data:
                return UserStackResponse(**cache_data)

            # Step 2: Query Userstack API
            response = requests.get(
                self.BASE_URL,
                params={
                    'access_key': self.api_key,
                    'ua': identifier
                },
                timeout=5
            )
            response.raise_for_status()
            response_data = response.json()

            # Optional: Validate using Pydantic
            try:
                validated_data = UserStackResponse(**response_data)
            except Exception as parse_error:
                print(f'Warning: Failed to parse UserStack response: {parse_error}')
                validated_data = None

            # Step 3: Cache the response
            self.put_cache_data(identifier, response_data)

            return validated_data

        except requests.RequestException as e:
            print(f'Error querying UserStack API: {e}')
            return None
        except Exception as e:
            print(f'Unexpected error: {e}')
            return None


############################
#  IP Geolocation models  ##
############################

class CurrencyInfo(BaseModel):
    code: Optional[str]
    name: Optional[str]
    symbol: Optional[str]

class DSTInfo(BaseModel):
    utc_time: Optional[str]
    duration: Optional[str]
    gap: Optional[bool]
    dateTimeAfter: Optional[str]
    dateTimeBefore: Optional[str]
    overlap: Optional[bool]

class TimeZoneInfo(BaseModel):
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

class IPGeolocationApiClient(BaseApiClient):
    BASE_URL = 'https://api.ipgeolocation.io/ipgeo'

    def __init__(self, api_key: str):
        # Use separate Redis DB for ip geolocation cache
        super().__init__(redis_db=4, redis_prefix='ip_geolocation')
        self.api_key = api_key

    def get_data(self, identifier: str) -> Optional[IPGeolocationResponse]:
        """Get IP geolocation data from the API."""
        try:
            # Check cache first
            cache_data = self.get_cache_data(identifier)

            if cache_data:
                return IPGeolocationResponse(**cache_data)

            # Query API
            response = requests.get(
                self.BASE_URL,
                params={
                    'apiKey': self.api_key,
                    'ip': identifier,
                    'output': 'json'
                },
                timeout=5
            )

            response.raise_for_status()
            response_data = response.json()

            # Optional: Validate using Pydantic
            try:
                validated_data = IPGeolocationResponse(**response_data)
            except Exception as parse_error:
                print(f'Warning: Failed to parse IPGeolocation response: {parse_error}')
                validated_data = None

            # Step 3: Cache the response
            self.put_cache_data(identifier, response_data)

            return validated_data

        except requests.RequestException as e:
            print(f'Error querying IPGeolocation API: {e}')
            return None
        except Exception as e:
            print(f'Unexpected error: {e}')
            return None


#####################
#  VPN API models  ##
#####################

class SecurityInfo(BaseModel):
    vpn: bool = False
    proxy: bool = False
    tor: bool = False
    relay: bool = False
    hosting: bool = False

class VpnApiResponse(BaseModel):
    ip: str
    security: SecurityInfo = Field(default_factory=SecurityInfo)

class VpnApiClient(BaseApiClient):
    BASE_URL = 'https://vpnapi.io/api'

    def __init__(self, api_key: str):
        # Use separate Redis DB for vpn cache
        super().__init__(redis_db=5, redis_prefix='vpn')
        self.api_key = api_key

    def get_data(self, identifier: str) -> Optional[VpnApiResponse]:
        print(f'Testing ip_address: {identifier}')
        print(f'Testing api key: {self.api_key}')

        try:
            # Check cache first
            cache_data = self.get_cache_data(identifier)

            if cache_data:
                print(f"cache response data: {cache_data}")
                return VpnApiResponse(**cache_data)

            # Query API
            response = requests.get(
                f'{self.BASE_URL}/{identifier}',
                params={'key': self.api_key},
                timeout=5
            )

            response.raise_for_status()
            response_data = response.json()

            print(f"response data: {response_data}")

            # Optional: Validate using Pydantic
            try:
                validated_data = VpnApiResponse(**response_data)
            except Exception as parse_error:
                print(f'Warning: Failed to parse VPN API response: {parse_error}')
                validated_data = None

            # Step 3: Cache the response
            self.put_cache_data(identifier, response_data)

            return validated_data

        except requests.RequestException as e:
            print(f'Error querying VPN API: {e}')
            return None

        except Exception as e:
            print(f'Error parsing VPN API.io response: {e}')
            return None

