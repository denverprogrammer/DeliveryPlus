"""API clients for various external services with Redis caching."""

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Dict, Optional, TypeVar, Generic

import json
import redis
import requests
from pydantic import BaseModel
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client as TwilioClient
from common.types import (
    IPGeolocationResponse,
    IpStackResponse,
    TwilioLookupResponse,
    UserStackResponse,
    VpnApiResponse,
)


ClientType = TypeVar("ClientType", bound=BaseModel)


class BaseApiClient(ABC, Generic[ClientType]):
    """Base class for API clients with Redis caching functionality."""

    def __init__(self, redis_db: int, redis_prefix: str) -> None:
        """Initialize the API client with Redis connection.

        Args:
            redis_db: Redis database number
            redis_prefix: Prefix for Redis keys
        """
        self.redis_client = redis.Redis(host="redis", port=6379, db=redis_db, decode_responses=True)
        self.redis_prefix = redis_prefix

    def get_cache_key(self, identifier: str) -> str:
        """Get the Redis cache key for an identifier.

        Args:
            identifier: The identifier to create a cache key for

        Returns:
            The cache key string
        """
        return f"{self.redis_prefix}:{identifier}"

    def get_cache_data(self, identifier: str) -> Optional[ClientType]:
        """Get cached data for an identifier.

        Args:
            identifier: The identifier to get cached data for

        Returns:
            The cached data or None if not found
        """
        value = self.redis_client.get(self.get_cache_key(identifier))
        if not value:
            return None
        try:
            data = json.loads(value)
            return self._parse_response(data)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing cached data: {e}")
            return None

    def put_cache_data(
        self, identifier: str, data: Dict[str, Any], ttl_seconds: int = 3600
    ) -> bool:
        """Put data in the cache with a TTL.

        Args:
            identifier: The identifier to cache data for
            data: The data to cache
            ttl_seconds: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        return self.redis_client.setex(
            self.get_cache_key(identifier), timedelta(seconds=ttl_seconds), json.dumps(data)
        )

    def _parse_response(self, data: Dict[str, Any]) -> ClientType:
        """Parse API response data into the appropriate model.

        Args:
            data: The response data to parse

        Returns:
            The parsed model instance

        Raises:
            ValueError: If the data cannot be parsed into the model
        """
        try:
            return self._get_response_model()(**data)
        except Exception as e:
            raise ValueError(f"Failed to parse response data: {e}")

    @abstractmethod
    def _get_response_model(self) -> type[ClientType]:
        """Get the response model class for this API client.

        Returns:
            The response model class
        """
        pass

    @abstractmethod
    def get_data(self, identifier: str) -> Optional[ClientType]:
        """Get data from the API or cache.

        Args:
            identifier: The identifier to get data for

        Returns:
            The data or None if not found
        """
        pass


######################
#  IP Stack models  ##
######################


class IpStackApiClient(BaseApiClient[IpStackResponse]):
    """Client for IP Stack API with Redis caching."""

    BASE_URL = "http://api.ipstack.com/"

    def __init__(self, api_key: str) -> None:
        """Initialize the IP Stack API client.

        Args:
            api_key: IP Stack API key
        """
        super().__init__(redis_db=1, redis_prefix="ip_address")
        self.api_key = api_key

    def _get_response_model(self) -> type[IpStackResponse]:
        """Get the response model class for this API client."""
        return IpStackResponse

    def get_data(self, identifier: str) -> Optional[IpStackResponse]:
        """Get IP address data from IP Stack API.

        Args:
            identifier: IP address to look up

        Returns:
            IP address data or None if not found
        """
        try:
            cache_data = self.get_cache_data(identifier)
            if cache_data:
                return cache_data

            response = requests.get(
                f"{self.BASE_URL}{identifier}", params={"access_key": self.api_key}, timeout=5
            )
            response.raise_for_status()

            response_data = response.json()
            self.put_cache_data(identifier, response_data)

            return self._parse_response(response_data)

        except requests.RequestException as e:
            print(f"Error querying IpStack API: {e}")
            return None
        except Exception as e:
            print(f"Error parsing IpStack API response: {e}")
            return None


##########################
#  TwilioLookup models  ##
##########################


class TwilioApiClient(BaseApiClient[TwilioLookupResponse]):
    """Client for Twilio Lookup API with Redis caching."""

    def __init__(self, account_sid: str, auth_token: str) -> None:
        """Initialize the Twilio API client.

        Args:
            account_sid: Twilio account SID
            auth_token: Twilio auth token
        """
        super().__init__(redis_db=2, redis_prefix="phone_number")
        self.client = TwilioClient(account_sid, auth_token)

    def _get_response_model(self) -> type[TwilioLookupResponse]:
        """Get the response model class for this API client."""
        return TwilioLookupResponse

    def get_data(self, identifier: str) -> Optional[TwilioLookupResponse]:
        """Get phone number data from Twilio Lookup API.

        Args:
            identifier: Phone number to look up

        Returns:
            Phone number data or None if not found

        Raises:
            TwilioRestException: If there's an error with the Twilio API
        """
        try:
            cache_data = self.get_cache_data(identifier)
            if cache_data:
                return cache_data

            response = self.client.lookups.v2.phone_numbers(identifier).fetch(
                fields=[
                    "caller_name",
                    "sim_swap",
                    "call_forwarding",
                    "line_status",
                    "line_type_intelligence",
                    "identity_match",
                    "reassigned_number",
                    "sms_pumping_risk",
                    "phone_number_quality_score",
                    "pre_fill",
                ]
            )

            response_data = response.__dict__
            response_data.pop("_version", None)
            response_data.pop("url", None)
            self.put_cache_data(identifier, response_data)

            return self._parse_response(response_data)

        except TwilioRestException as e:
            if e.code == 20404:
                return None
            print(f"Error querying Twilio Lookup API: {e}")
            raise e


#######################
#  UserStack models  ##
#######################


class UserStackApiClient(BaseApiClient[UserStackResponse]):
    """Client for UserStack API with Redis caching."""

    BASE_URL = "http://api.userstack.com/detect"

    def __init__(self, api_key: str) -> None:
        """Initialize the UserStack API client.

        Args:
            api_key: UserStack API key
        """
        super().__init__(redis_db=3, redis_prefix="user_agent")
        self.api_key = api_key

    def _get_response_model(self) -> type[UserStackResponse]:
        """Get the response model class for this API client."""
        return UserStackResponse

    def get_data(self, identifier: str) -> Optional[UserStackResponse]:
        """Get user agent data from UserStack API.

        Args:
            identifier: User agent string to look up

        Returns:
            User agent data or None if not found
        """
        try:
            cache_data = self.get_cache_data(identifier)
            if cache_data:
                return cache_data

            response = requests.get(
                self.BASE_URL, params={"access_key": self.api_key, "ua": identifier}, timeout=5
            )
            response.raise_for_status()
            response_data = response.json()

            self.put_cache_data(identifier, response_data)
            return self._parse_response(response_data)

        except requests.RequestException as e:
            print(f"Error querying UserStack API: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None


############################
#  IP Geolocation models  ##
############################


class IPGeolocationApiClient(BaseApiClient[IPGeolocationResponse]):
    """Client for IP Geolocation API with Redis caching."""

    BASE_URL = "https://api.ipgeolocation.io/ipgeo"

    def __init__(self, api_key: str) -> None:
        """Initialize the IP Geolocation API client.

        Args:
            api_key: IP Geolocation API key
        """
        super().__init__(redis_db=4, redis_prefix="ip_geolocation")
        self.api_key = api_key

    def _get_response_model(self) -> type[IPGeolocationResponse]:
        """Get the response model class for this API client."""
        return IPGeolocationResponse

    def get_data(self, identifier: str) -> Optional[IPGeolocationResponse]:
        """Get IP geolocation data from the API.

        Args:
            identifier: IP address to look up

        Returns:
            IP geolocation data or None if not found
        """
        try:
            cache_data = self.get_cache_data(identifier)
            if cache_data:
                return cache_data

            response = requests.get(
                self.BASE_URL,
                params={"apiKey": self.api_key, "ip": identifier, "output": "json"},
                timeout=30,
            )

            response.raise_for_status()
            response_data = response.json()

            self.put_cache_data(identifier, response_data)
            return self._parse_response(response_data)

        except requests.RequestException as e:
            print(f"Error querying IPGeolocation API: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None


#####################
#  VPN API models  ##
#####################


class VpnApiClient(BaseApiClient[VpnApiResponse]):
    """Client for VPN API with Redis caching."""

    BASE_URL = "https://vpnapi.io/api"

    def __init__(self, api_key: str) -> None:
        """Initialize the VPN API client.

        Args:
            api_key: VPN API key
        """
        super().__init__(redis_db=5, redis_prefix="vpn")
        self.api_key = api_key

    def _get_response_model(self) -> type[VpnApiResponse]:
        """Get the response model class for this API client."""
        return VpnApiResponse

    def get_data(self, identifier: str) -> Optional[VpnApiResponse]:
        """Get VPN detection data from the API.

        Args:
            identifier: IP address to check

        Returns:
            VPN detection data or None if not found
        """
        try:
            cache_data = self.get_cache_data(identifier)
            if cache_data:
                return cache_data

            response = requests.get(
                f"{self.BASE_URL}/{identifier}", params={"key": self.api_key}, timeout=5
            )

            response.raise_for_status()
            response_data = response.json()

            self.put_cache_data(identifier, response_data)
            return self._parse_response(response_data)

        except requests.RequestException as e:
            print(f"Error querying VPN API: {e}")
            return None
        except Exception as e:
            print(f"Error parsing VPN API.io response: {e}")
            return None
