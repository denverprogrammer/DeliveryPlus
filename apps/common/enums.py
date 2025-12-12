"""Common enums used across the application."""

from __future__ import annotations
from enum import Enum
from typing import List
from typing import Tuple


class TrackingType(str, Enum):
    SERVER = "server"
    HEADER = "client"

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(key.value, key.name.title()) for key in cls]


class RecipientStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(key.value, key.name.title()) for key in cls]


class PublishingType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(key.value, key.name.title()) for key in cls]


class TokenStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(key.value, key.name.title()) for key in cls]
