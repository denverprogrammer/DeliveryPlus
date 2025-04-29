from __future__ import annotations
from django.db import models
from tracking.common import AgentStatus, TrackingType
from typing import Optional, Dict, Any
from tracking.api.types import IpData, UserAgentData
from config.common import HeaderData


class Campaign(models.Model):
    company = models.ForeignKey(
        'mgmt.Company',
        on_delete=models.CASCADE,
        related_name='campaigns',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    publishing_type = models.JSONField(default=list, blank=True, null=True)
    landing_page_url = models.URLField(blank=True, null=True)
    tracking_pixel = models.TextField(blank=True, null=True)

    ip_precedence = models.CharField(
        max_length=10,
        choices=TrackingType.choices(),
        default=TrackingType.SERVER,
        help_text="Determines whether to use server or client IP for tracking"
    )

    location_precedence = models.CharField(
        max_length=10,
        choices=TrackingType.choices(),
        default=TrackingType.SERVER,
        help_text="Determines whether to use server or client location for tracking"
    )

    locale_precedence = models.CharField(
        max_length=10,
        choices=TrackingType.choices(),
        default=TrackingType.SERVER,
        help_text="Determines whether to use server or client locale for tracking"
    )

    browser_precedence = models.CharField(
        max_length=10,
        choices=TrackingType.choices(),
        default=TrackingType.SERVER,
        help_text="Determines whether to use server or client browser information for tracking"
    )

    time_precedence = models.CharField(
        max_length=10,
        choices=TrackingType.choices(),
        default=TrackingType.SERVER,
        help_text="Determines whether to use server or client time for tracking"
    )

    ip_tracking = models.JSONField(default=list, blank=True, null=True)
    location_tracking = models.JSONField(default=list, blank=True, null=True)
    locale_tracking = models.JSONField(default=list, blank=True, null=True)
    time_tracking = models.JSONField(default=list, blank=True, null=True)
    browser_tracking = models.JSONField(default=list, blank=True, null=True)
    # has_phone = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class Agent(models.Model):
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='agents'
    )
    token = models.CharField(max_length=255)

    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    status = models.CharField(
        max_length=10,
        choices=AgentStatus.choices(),
        default=AgentStatus.ACTIVE.value
    )

    def __str__(self):
        return f'{self.first_name or ""} {self.last_name or ""}'.strip() or self.token


class TrackingData(models.Model):
    agent = models.ForeignKey(Agent, related_name='tracking', on_delete=models.CASCADE)
    http_method = models.CharField(max_length=10)
    server_timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    ip_source = models.CharField(
        max_length=10,
        choices=TrackingType.choices(),
        null=True,
        blank=True
    )
    os = models.CharField(max_length=100, null=True, blank=True)
    browser = models.CharField(max_length=100, null=True, blank=True)
    platform = models.CharField(max_length=100, null=True, blank=True)
    locale = models.CharField(max_length=10, null=True, blank=True)
    client_time = models.DateTimeField(null=True, blank=True)
    client_timezone = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_source = models.CharField(
        max_length=10,
        choices=TrackingType.choices(),
        null=True,
        blank=True
    )
    _ip_data = models.JSONField(null=True, blank=True, db_column='ip_data')
    _user_agent_data = models.JSONField(null=True, blank=True, db_column='user_agent_data')
    _header_data  = models.JSONField(null=True, blank=True, db_column='header_data ')
    _form_data = models.JSONField(null=True, blank=True, db_column='form_data')
    
    # phone_data = models.JSONField(null=True, blank=True)

    @property
    def ip_data(self) -> Optional[IpData]:
        if not self._ip_data:
            return None
        return IpData.model_validate(self._ip_data)

    @ip_data.setter
    def ip_data(self, value: Optional[IpData]):
        self._ip_data = value.model_dump() if value else None

    @property
    def user_agent_data(self) -> Optional[UserAgentData]:
        if not self._user_agent_data:
            return None
        return UserAgentData.model_validate(self._user_agent_data)

    @user_agent_data.setter
    def user_agent_data(self, value: Optional[UserAgentData]):
        self._user_agent_data = value.model_dump() if value else None

    @property
    def header_data (self) -> Optional[HeaderData]:
        if not self._header_data :
            return None
        return HeaderData.model_validate(self._header_data)

    @header_data .setter
    def header_data (self, value: Optional[HeaderData]):
        self._header_data  = value.model_dump() if value else None

    @property
    def form_data(self) -> Optional[Dict[str, Any]]:
        return self._form_data

    @form_data.setter
    def form_data(self, value: Optional[Dict[str, Any]]):
        self._form_data = value

    @property
    def ip_checks(self) -> dict[str, dict[str, str]]:
        """Check for VPN, proxy, and Tor usage."""
        return {
            'vpn': {
                'status': 'warning' if self.ip_data and self.ip_data.isVpn() else 'success',
                'message': '⚠️ VPN usage detected' if self.ip_data and self.ip_data.isVpn() else '✅ No VPN detected'
            },
            'proxy': {
                'status': 'warning' if self.ip_data and self.ip_data.isProxy() else 'success',
                'message': '⚠️ Proxy usage detected' if self.ip_data and self.ip_data.isProxy() else '✅ No proxy detected'
            },
            'tor': {
                'status': 'warning' if self.ip_data and self.ip_data.isTor() else 'success',
                'message': '⚠️ Tor usage detected' if self.ip_data and self.ip_data.isTor() else '✅ No Tor detected'
            }
        }

    @property
    def ip_mismatch(self) -> dict[str, str]:
        """Check for IP address mismatches between server and client."""
        return {
            'status': 'warning' if self.ip_data and self.ip_data.getServerIpAddress() != self.ip_data.getHeaderIpAddress() else 'success',
            'message': '⚠️ IP Address Mismatch: Server IP differs from Header IP' if self.ip_data and self.ip_data.getServerIpAddress() != self.ip_data.getHeaderIpAddress() else '✅ IP addresses match'
        }

    @property
    def country_mismatch(self) -> dict[str, str]:
        """Check for country mismatches between server and client."""
        return {
            'status': 'warning' if self.ip_data and self.header_data and self.ip_data.getSelectedCountry() != self.header_data.getHeaderCountry() else 'success',
            'message': '⚠️ Country Mismatch: Server country differs from Header country' if self.ip_data and self.header_data and self.ip_data.getSelectedCountry() != self.header_data.getHeaderCountry() else '✅ Countries match'
        }

    @property
    def user_agent_mismatch(self) -> dict[str, str]:
        """Check for user agent mismatches."""
        return {
            'status': 'warning' if self.user_agent_data and self.user_agent_data.header != self.user_agent_data.server else 'success',
            'message': '⚠️ User Agent Mismatch: Server and Client user agents differ' if self.user_agent_data and self.user_agent_data.header != self.user_agent_data.server else '✅ User agents match'
        }

    @property
    def timezone_mismatch(self) -> dict[str, str]:
        """Check for timezone mismatches."""
        return {
            'status': 'warning' if self.ip_data and self.header_data and self.ip_data.getTimezone() != self.header_data.getTimezone() else 'success',
            'message': '⚠️ Timezone Mismatch: Header timezone differs from IP timezone' if self.ip_data and self.header_data and self.ip_data.getTimezone() != self.header_data.getTimezone() else '✅ Timezones match'
        }

    @property
    def locale_mismatch(self) -> dict[str, str]:
        """Check for locale mismatches between server and client."""
        return {
            'status': 'warning' if self.ip_data and self.header_data and self.ip_data.getLocales() and self.header_data.getLocale() and self.ip_data.getLocales()[0] != self.header_data.getLocale() else 'success',
            'message': '⚠️ Locale Mismatch: Server locale differs from Browser locale' if self.ip_data and self.header_data and self.ip_data.getLocales() and self.header_data.getLocale() and self.ip_data.getLocales()[0] != self.header_data.getLocale() else '✅ Locales match'
        }

    @property
    def crawler_detection(self) -> dict[str, str]:
        """Check for crawler/bot detection."""
        return {
            'status': 'warning' if self.user_agent_data and self.user_agent_data.is_crawler() else 'success',
            'message': '⚠️ Crawler/Bot Detected' if self.user_agent_data and self.user_agent_data.is_crawler() else '✅ No crawler detected'
        }

    @property
    def all_warnings(self) -> dict[str, Any]:
        """Get all warning checks."""
        return {
            'ip_checks': self.ip_checks,
            'ip_mismatch': self.ip_mismatch,
            'country_mismatch': self.country_mismatch,
            'user_agent_mismatch': self.user_agent_mismatch,
            'timezone_mismatch': self.timezone_mismatch,
            'locale_mismatch': self.locale_mismatch,
            'crawler_detection': self.crawler_detection
        }

    def __str__(self):
        return f'{self.agent} @ {self.server_timestamp.strftime("%Y-%m-%d %H:%M:%S")}'
