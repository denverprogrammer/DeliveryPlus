# tracker/models.py
from __future__ import annotations
from typing import List, Tuple
from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum

class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(key.value, key.name.title()) for key in cls]

class Company(models.Model):
    name: str = models.CharField(max_length=255)
    street_address: str = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state: str = models.CharField(max_length=100, blank=True, null=True)
    zip_code: str = models.CharField(max_length=20, blank=True, null=True)
    country: str = models.CharField(max_length=100, blank=True, null=True)
    phone_number: str = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self) -> str:
        return self.name

class User(AbstractUser):
    company: Company | None = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )

class Agent(models.Model):
    company: Company | None = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="agents", null=True, blank=True
    )
    token: str = models.CharField(max_length=255)
    phone_number: str = models.CharField(max_length=20, blank=True, null=True)
    first_name: str = models.CharField(max_length=100, blank=True, null=True)
    last_name: str = models.CharField(max_length=100, blank=True, null=True)
    email: str = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    notifications = models.CharField(max_length=20, blank=True, null=True)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    status: str = models.CharField(
        max_length=10, choices=AgentStatus.choices(), default=AgentStatus.ACTIVE.value
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

class TrackingData(models.Model):
    agent = models.ForeignKey("Agent", related_name="tracking", on_delete=models.CASCADE)
    http_method = models.CharField(max_length=10)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    server_timestamp = models.DateTimeField(auto_now_add=True)
    client_timestamp = models.DateTimeField(blank=True, null=True)
    client_timezone = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    # def __str__(self):
    #     return f"{self.agent} - {self.server_timestamp} - {self.ip_address}"
