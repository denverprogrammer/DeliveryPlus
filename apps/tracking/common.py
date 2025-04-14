from __future__ import annotations
import json
from typing import List, Tuple
from django.db import models
from enum import Enum


class TrackingType(str, Enum):
    SERVER = 'server'
    CLIENT = 'client'

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(key.value, key.name.title()) for key in cls]


class AgentStatus(str, Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(key.value, key.name.title()) for key in cls]


class PublishingType(str, Enum):
    EMAIL = 'email'
    PHONE = 'phone'

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(key.value, key.name.title()) for key in cls]

