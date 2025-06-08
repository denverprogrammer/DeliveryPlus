from __future__ import annotations
from typing import Optional
from django.contrib.auth.models import AbstractUser
from django.db import models
from django_stubs_ext.db.models import TypedModelMeta


class Company(models.Model):
    name: models.CharField[str, str] = models.CharField(max_length=255)
    street_address: models.CharField[str, Optional[str]] = models.CharField(
        max_length=255, blank=True, null=True
    )
    city: models.CharField[str, Optional[str]] = models.CharField(
        max_length=100, blank=True, null=True
    )
    state: models.CharField[str, Optional[str]] = models.CharField(
        max_length=100, blank=True, null=True
    )
    zip_code: models.CharField[str, Optional[str]] = models.CharField(
        max_length=20, blank=True, null=True
    )
    country: models.CharField[str, Optional[str]] = models.CharField(
        max_length=100, blank=True, null=True
    )
    phone_number: models.CharField[str, Optional[str]] = models.CharField(
        max_length=20, blank=True, null=True
    )

    class Meta(TypedModelMeta):
        verbose_name_plural = "Companies"

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    company: models.ForeignKey[Company, Optional[Company]] = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )
