from __future__ import annotations
from django.db import models
from django.utils import timezone
import json
from tracking.common import AgentStatus, TrackingType


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
    agent = models.ForeignKey('Agent', related_name='tracking', on_delete=models.CASCADE)
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
    ip_data = models.JSONField(null=True, blank=True)
    user_agent_data = models.JSONField(null=True, blank=True)
    headers_data = models.JSONField(null=True, blank=True)
    tracking_data = models.JSONField(null=True, blank=True)
    form_data = models.JSONField(null=True, blank=True)
    
    # phone_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.agent} @ {self.server_timestamp.strftime("%Y-%m-%d %H:%M:%S")}'
