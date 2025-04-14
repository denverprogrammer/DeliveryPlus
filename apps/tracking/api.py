from datetime import timedelta
from pydantic import BaseModel
import requests
from typing import Optional
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


class OSInfo(BaseModel):
    name: Optional[str]
    code: Optional[str]
    version: Optional[str]


class DeviceInfo(BaseModel):
    type: Optional[str]
    brand: Optional[str]
    name: Optional[str]


class BrowserInfo(BaseModel):
    name: Optional[str]
    version: Optional[str]


class UserStackResponse(BaseModel):
    user_agent: Optional[str]
    os: Optional[OSInfo]
    device: Optional[DeviceInfo]
    browser: Optional[BrowserInfo]
    crawler: Optional[bool]


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


class VPNApiClient:
    BASE_URL = 'https://vpnapi.io/api/'

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_vpn_data(self, ip_address: str) -> Optional[str]:
        print(f'Testing ip_address: {ip_address}')
        print(f'Testing api key: {self.api_key}')
        
        url = f'{self.BASE_URL}{ip_address}'
        params = {'key': self.api_key}

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            response_data = response.json()
            
            print(f'api response: {response_data}')
            
            return response_data
            
            # vpn_data = IpData(**response_data)

            # return vpn_data

        except requests.RequestException as e:
            print(f'Error querying VPN API: {e}')
            return None

        except Exception as e:
            print(f'Error parsing VPN API.io response: {e}')
            return None


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


class UserStackApiClient(BaseApiClient):
    BASE_URL = 'http://api.userstack.com/detect'

    def __init__(self, api_key: str):
        # Use separate Redis DB for user-agent cache
        super().__init__(redis_db=3, redis_prefix='user_agent')
        self.api_key = api_key

    def get_data(self, identifier: str) -> Optional[dict[str, Any]]:
        try:
            # Step 1: Check cache first
            cache_data = self.get_cache_data(identifier)
            if cache_data:
                return cache_data

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
                validated_data = response_data  # Fallback to raw

            # Step 3: Cache the response
            self.put_cache_data(identifier, response_data)

            return response_data

        except requests.RequestException as e:
            print(f'Error querying UserStack API: {e}')
            return None
        except Exception as e:
            print(f'Unexpected error: {e}')
            return None
