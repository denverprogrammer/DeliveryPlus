from __future__ import annotations
import datetime

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import TypeVar
from common.api_types import HeaderData
from common.api_types import IpData
from common.api_types import UserAgentData
from common.api_types import WarningStatus
from common.enums import AgentStatus
from common.enums import TrackingType
from django.db import models
from django.db.models import Manager
from django.db.models import Model
from django_stubs_ext.db.models import TypedModelMeta
from mgmt.models import Company
from taggit.managers import TaggableManager


T = TypeVar("T", bound=Model)


class Campaign(models.Model):
    company: models.ForeignKey[Company, Optional[Company]] = models.ForeignKey(
        "mgmt.Company", on_delete=models.CASCADE, related_name="campaigns"
    )
    name: models.CharField[str, str] = models.CharField(max_length=255)
    description: models.TextField[str, Optional[str]] = models.TextField(blank=True, null=True)

    publishing_type: models.JSONField[list[Any], Optional[list[Any]]] = models.JSONField(
        default=list, blank=True, null=True
    )
    landing_page_url: models.URLField[str, Optional[str]] = models.URLField(blank=True, null=True)
    tracking_pixel: models.TextField[str, Optional[str]] = models.TextField(blank=True, null=True)

    ip_precedence: models.CharField[str, str] = models.CharField(
        max_length=10,
        choices=TrackingType.choices(),
        default=TrackingType.SERVER,
        help_text="Determines whether to use server or client IP for tracking",
    )

    location_precedence: models.CharField[str, str] = models.CharField(
        max_length=10,
        choices=TrackingType.choices(),
        default=TrackingType.SERVER,
        help_text="Determines whether to use server or client location for tracking",
    )

    locale_precedence: models.CharField[str, str] = models.CharField(
        max_length=10,
        choices=TrackingType.choices(),
        default=TrackingType.SERVER,
        help_text="Determines whether to use server or client locale for tracking",
    )

    browser_precedence: models.CharField[str, str] = models.CharField(
        max_length=10,
        choices=TrackingType.choices(),
        default=TrackingType.SERVER,
        help_text="Determines whether to use server or client browser information for tracking",
    )

    time_precedence: models.CharField[str, str] = models.CharField(
        max_length=10,
        choices=TrackingType.choices(),
        default=TrackingType.SERVER,
        help_text="Determines whether to use server or client time for tracking",
    )

    ip_tracking: models.JSONField[list[Any], Optional[list[Any]]] = models.JSONField(
        default=list, blank=True, null=True
    )
    location_tracking: models.JSONField[list[Any], Optional[list[Any]]] = models.JSONField(
        default=list, blank=True, null=True
    )
    locale_tracking: models.JSONField[list[Any], Optional[list[Any]]] = models.JSONField(
        default=list, blank=True, null=True
    )
    time_tracking: models.JSONField[list[Any], Optional[list[Any]]] = models.JSONField(
        default=list, blank=True, null=True
    )
    browser_tracking: models.JSONField[list[Any], Optional[list[Any]]] = models.JSONField(
        default=list, blank=True, null=True
    )
    # has_phone = models.BooleanField(default=False)

    objects: Manager[Campaign] = Manager["Campaign"]()

    class Meta(TypedModelMeta):
        verbose_name_plural = "Campaigns"

    def __str__(self) -> str:
        return self.name


class Agent(models.Model):
    campaign: models.ForeignKey[Campaign, Campaign] = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="agents"
    )
    token: models.CharField[str, str] = models.CharField(max_length=255)

    first_name: models.CharField[str, Optional[str]] = models.CharField(
        max_length=100, blank=True, null=True
    )
    last_name: models.CharField[str, Optional[str]] = models.CharField(
        max_length=100, blank=True, null=True
    )
    email: models.EmailField[str, Optional[str]] = models.EmailField(blank=True, null=True)
    phone_number: models.CharField[str, Optional[str]] = models.CharField(
        max_length=20, blank=True, null=True
    )
    status: models.CharField[str, str] = models.CharField(
        max_length=10, choices=AgentStatus.choices(), default=AgentStatus.ACTIVE.value
    )
    tags = TaggableManager(
        help_text="Enter tags to categorize this agent (max 10 tags)",
        blank=True,
    )

    objects: Manager[Agent] = Manager["Agent"]()

    class Meta(TypedModelMeta):
        verbose_name_plural = "Agents"

    def __str__(self) -> str:
        return f'{self.first_name or ""} {self.last_name or ""}'.strip() or self.token


class TrackingData(models.Model):
    agent: models.ForeignKey[Agent, Agent] = models.ForeignKey(
        Agent, related_name="tracking", on_delete=models.CASCADE
    )
    http_method: models.CharField[str, str] = models.CharField(max_length=10)
    server_timestamp: models.DateTimeField[datetime.datetime, datetime.datetime] = (
        models.DateTimeField(auto_now_add=True)
    )
    ip_address: models.GenericIPAddressField[Optional[str], Optional[str]] = (
        models.GenericIPAddressField(null=True, blank=True)
    )
    ip_source: models.CharField[Optional[str], Optional[str]] = models.CharField(
        max_length=10, choices=TrackingType.choices(), null=True, blank=True
    )
    os: models.CharField[Optional[str], Optional[str]] = models.CharField(
        max_length=100, null=True, blank=True
    )
    browser: models.CharField[Optional[str], Optional[str]] = models.CharField(
        max_length=100, null=True, blank=True
    )
    platform: models.CharField[Optional[str], Optional[str]] = models.CharField(
        max_length=100, null=True, blank=True
    )
    locale: models.CharField[Optional[str], Optional[str]] = models.CharField(
        max_length=10, null=True, blank=True
    )
    client_time: models.DateTimeField[Optional[datetime.datetime], Optional[datetime.datetime]] = (
        models.DateTimeField(null=True, blank=True)
    )
    client_timezone: models.CharField[Optional[str], Optional[str]] = models.CharField(
        max_length=50, null=True, blank=True
    )
    latitude: models.FloatField[Optional[float], Optional[float]] = models.FloatField(
        null=True, blank=True
    )
    longitude: models.FloatField[Optional[float], Optional[float]] = models.FloatField(
        null=True, blank=True
    )
    location_source: models.CharField[Optional[str], Optional[str]] = models.CharField(
        max_length=10, choices=TrackingType.choices(), null=True, blank=True
    )
    _ip_data: models.JSONField[Optional[dict[str, Any]], Optional[dict[str, Any]]] = (
        models.JSONField(null=True, blank=True, db_column="ip_data")
    )
    _user_agent_data: models.JSONField[Optional[dict[str, Any]], Optional[dict[str, Any]]] = (
        models.JSONField(null=True, blank=True, db_column="user_agent_data")
    )
    _header_data: models.JSONField[Optional[dict[str, Any]], Optional[dict[str, Any]]] = (
        models.JSONField(null=True, blank=True, db_column="header_data ")
    )
    _form_data: models.JSONField[Optional[dict[str, Any]], Optional[dict[str, Any]]] = (
        models.JSONField(null=True, blank=True, db_column="form_data")
    )

    # phone_data = models.JSONField(null=True, blank=True)

    class Meta(TypedModelMeta):
        verbose_name_plural = "Tracking Data"

    @property
    def ip_data(self) -> Optional[IpData]:
        if not self._ip_data:
            return None
        return IpData.model_validate(self._ip_data)

    @ip_data.setter
    def ip_data(self, value: Optional[IpData]) -> None:
        self._ip_data = value.model_dump() if value else None

    @property
    def user_agent_data(self) -> Optional[UserAgentData]:
        if not self._user_agent_data:
            return None
        return UserAgentData.model_validate(self._user_agent_data)

    @user_agent_data.setter
    def user_agent_data(self, value: Optional[UserAgentData]) -> None:
        self._user_agent_data = value.model_dump() if value else None

    @property
    def header_data(self) -> Optional[HeaderData]:
        if not self._header_data:
            return None
        return HeaderData.model_validate(self._header_data)

    @header_data.setter
    def header_data(self, value: Optional[HeaderData]) -> None:
        self._header_data = value.model_dump() if value else None

    @property
    def form_data(self) -> Optional[Dict[str, Any]]:
        return self._form_data

    @form_data.setter
    def form_data(self, value: Optional[Dict[str, Any]]) -> None:
        self._form_data = value

    @property
    def security_checks(self) -> List[WarningStatus]:
        """Check for VPN, proxy, and Tor usage."""
        if not self.ip_data:
            return [
                WarningStatus(
                    status="warning",
                    category="security",
                    message="Security checks could not be set for ip address",
                )
            ]
        return self.ip_data.get_security_checks()

    @property
    def ip_mismatch(self) -> WarningStatus:
        """Check for IP address mismatches between server and client."""
        if not self.ip_data:
            return WarningStatus(status="warning", message="IP Address could not be set")
        return self.ip_data.get_ip_mismatch()

    @property
    def country_mismatch(self) -> WarningStatus:
        """Check for country mismatches between server and client."""
        if not self.ip_data:
            return WarningStatus(status="warning", message="IP Address could not be set")
        return self.ip_data.get_country_mismatch()

    @property
    def user_agent_mismatch(self) -> WarningStatus:
        """Check for user agent mismatches."""
        if not self.user_agent_data:
            return WarningStatus(status="warning", message="User Agent data could not be set")
        return self.user_agent_data.get_user_agent_mismatch()

    @property
    def timezone_mismatch(self) -> WarningStatus:
        """Check for timezone mismatches."""
        if not self.ip_data:
            return WarningStatus(status="warning", message="IP Address could not be set")
        return self.ip_data.get_timezone_mismatch()

    @property
    def locale_mismatch(self) -> WarningStatus:
        """Check for locale mismatches between server and client."""
        if not self.ip_data:
            return WarningStatus(status="warning", message="IP Address could not be set")
        return self.ip_data.get_locale_mismatch()

    @property
    def crawler_detection(self) -> WarningStatus:
        """Check for crawler/bot detection."""
        if not self.user_agent_data:
            return WarningStatus(status="warning", message="User Agent data could not be set")
        return self.user_agent_data.get_crawler_detection()

    @property
    def all_warnings(self) -> dict[str, Any]:
        """Get all warning checks."""
        return {
            "security_checks": self.security_checks,
            "ip_mismatch": self.ip_mismatch.model_dump(),
            "country_mismatch": self.country_mismatch.model_dump(),
            "user_agent_mismatch": self.user_agent_mismatch.model_dump(),
            "timezone_mismatch": self.timezone_mismatch.model_dump(),
            "locale_mismatch": self.locale_mismatch.model_dump(),
            "crawler_detection": self.crawler_detection.model_dump(),
        }

    def __str__(self) -> str:
        return f'{self.agent} @ {self.server_timestamp.strftime("%Y-%m-%d %H:%M:%S")}'
