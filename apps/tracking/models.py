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
from common.enums import CampaignDataType
from common.enums import ImageDataType
from common.enums import RecipientStatus
from common.enums import TokenStatus
from common.enums import TrackingDataType
from common.enums import TrackingType
from django.db import models
from django.db.models import Manager
from django.db.models import Model
from django.db.models import QuerySet
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
    campaign_type: models.CharField[str, str] = models.CharField(
        max_length=20,
        choices=CampaignDataType.choices(),
        db_index=True,
        default=CampaignDataType.PACKAGES.value,
        blank=False,
        null=False,
    )

    objects: Manager[Campaign] = Manager["Campaign"]()

    class Meta(TypedModelMeta):
        verbose_name_plural = "Campaigns"

    def __str__(self) -> str:
        return self.name


class Recipient(models.Model):
    company: models.ForeignKey[Company, Optional[Company]] = models.ForeignKey(
        "mgmt.Company", on_delete=models.CASCADE, related_name="recipients"
    )

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
        max_length=10, choices=RecipientStatus.choices(), default=RecipientStatus.ACTIVE.value
    )

    tags = TaggableManager(
        help_text="Enter tags to categorize this recipient (max 10 tags)",
        blank=True,
    )

    objects: Manager[Recipient] = Manager["Recipient"]()

    class Meta(TypedModelMeta):
        verbose_name_plural = "Recipients"

    def __str__(self) -> str:
        name = f'{self.first_name or ""} {self.last_name or ""}'.strip()
        return name or f"Recipient #{self.id}"


class Token(models.Model):
    tracking: models.ForeignKey["Tracking", "Tracking"] = models.ForeignKey(
        "Tracking", on_delete=models.CASCADE, related_name="tokens"
    )

    value: models.CharField[str, str] = models.CharField(max_length=255, unique=True)

    status: models.CharField[str, str] = models.CharField(
        max_length=10, choices=TokenStatus.choices(), default=TokenStatus.ACTIVE.value
    )

    created_on: models.DateTimeField[datetime.datetime, datetime.datetime] = models.DateTimeField(
        auto_now_add=True
    )

    deleted_on: models.DateTimeField[Optional[datetime.datetime], Optional[datetime.datetime]] = (
        models.DateTimeField(null=True, blank=True)
    )

    last_used: models.DateTimeField[Optional[datetime.datetime], Optional[datetime.datetime]] = (
        models.DateTimeField(null=True, blank=True)
    )

    objects: Manager[Token] = Manager["Token"]()

    class Meta(TypedModelMeta):
        verbose_name_plural = "Tokens"

    def __str__(self) -> str:
        return self.value


class Tracking(models.Model):
    campaign: models.ForeignKey[Campaign, Campaign] = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="tracking"
    )

    recipient: models.ForeignKey[Recipient, Recipient] = models.ForeignKey(
        Recipient, on_delete=models.CASCADE, related_name="tracking"
    )

    company: models.ForeignKey[Company, Optional[Company]] = models.ForeignKey(
        "mgmt.Company", on_delete=models.CASCADE, related_name="tracking"
    )

    objects: Manager[Tracking] = Manager["Tracking"]()

    @property
    def count_requests(self) -> Optional[int]:
        """Count the total number of records that reference this token."""
        if not self.pk or not self.campaign:
            return None
        elif self.campaign.campaign_type == CampaignDataType.PACKAGES.value:
            return int(self.tracking_request_data.count())
        elif self.campaign.campaign_type == CampaignDataType.IMAGES.value:
            return int(self.image_request_data.count())
        else:
            return None

    class Meta(TypedModelMeta):
        verbose_name_plural = "Tracking"

        def __str__(self) -> str:
            return f"Tracking #{self.id}"


##############################
#  Abstract Tracking Models  #
##############################


class AbstractRequestData(models.Model):

    RELATED_NAME = "abstract_request_data"

    tracking: models.ForeignKey[Tracking, Tracking] = models.ForeignKey(
        Tracking, related_name=RELATED_NAME, on_delete=models.CASCADE
    )

    token: models.ForeignKey["Token", "Token"] = models.ForeignKey(
        Token, related_name=RELATED_NAME, on_delete=models.CASCADE
    )

    # Common fields
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

    class Meta(TypedModelMeta):
        abstract = True

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

    @property
    def organization(self) -> Optional[str]:
        if self.ip_data:
            return self.ip_data.getSelectedISP()
        return None

    @property
    def isp(self) -> Optional[str]:
        if self.ip_data:
            return self.ip_data.getSelectedISP()
        return None

    @property
    def country(self) -> Optional[str]:
        if self.ip_data:
            return self.ip_data.getSelectedCountryName()
        return None

    @property
    def region(self) -> Optional[str]:
        if self.ip_data:
            return self.ip_data.getSelectedRegion()
        return None

    @property
    def city(self) -> Optional[str]:
        if self.ip_data:
            return self.ip_data.getSelectedCity()
        return None

    def __str__(self) -> str:
        return "Tracking data"


###############################
#  Package Tracking Managers  #
###############################


class TrackingDataManager(Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(data_type=TrackingDataType.TRACKING.value)


class NotificationDataManager(Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(data_type=TrackingDataType.NOTIFICATION.value)


class InterceptionDataManager(Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(data_type=TrackingDataType.INTERCEPTION.value)


#############################
#  Package Tracking Models  #
#############################


class TrackingRequestData(AbstractRequestData):

    RELATED_NAME = "tracking_request_data"

    # Discriminator field to identify the record type
    data_type: models.CharField[str, str] = models.CharField(
        max_length=20, choices=TrackingDataType.choices(), db_index=True
    )

    tracking: models.ForeignKey[Tracking, Tracking] = models.ForeignKey(
        Tracking, related_name=RELATED_NAME, on_delete=models.CASCADE
    )

    token: models.ForeignKey[Token, Token] = models.ForeignKey(
        Token, related_name=RELATED_NAME, on_delete=models.CASCADE
    )

    # NotificationData-specific fields
    _phone_data: models.JSONField[Optional[dict[str, Any]], Optional[dict[str, Any]]] = (
        models.JSONField(null=True, blank=True, db_column="phone_data")
    )

    # InterceptionData-specific fields
    recipient_name: models.CharField[str, Optional[str]] = models.CharField(
        max_length=255, blank=True, null=True
    )

    street_address_line_1: models.CharField[str, Optional[str]] = models.CharField(
        max_length=255, blank=True, null=True
    )

    street_address_line_2: models.CharField[str, Optional[str]] = models.CharField(
        max_length=255, blank=True, null=True
    )

    city: models.CharField[str, Optional[str]] = models.CharField(
        max_length=100, blank=True, null=True
    )

    state_province: models.CharField[str, Optional[str]] = models.CharField(
        max_length=100, blank=True, null=True
    )

    postal_code: models.CharField[str, Optional[str]] = models.CharField(
        max_length=20, blank=True, null=True
    )

    country: models.CharField[str, Optional[str]] = models.CharField(
        max_length=100, blank=True, null=True
    )

    _address_data: models.JSONField[Optional[dict[str, Any]], Optional[dict[str, Any]]] = (
        models.JSONField(null=True, blank=True, db_column="address_data")
    )

    objects: Manager["TrackingRequestData"] = Manager["TrackingRequestData"]()

    class Meta(TypedModelMeta):
        verbose_name_plural = "Tracking Request Data"
        indexes = [
            models.Index(fields=["data_type", "tracking"]),
            models.Index(fields=["data_type", "token"]),
        ]

    def __str__(self) -> str:
        return ""


class TrackingData(TrackingRequestData):
    objects = TrackingDataManager()

    class Meta(TypedModelMeta):
        proxy = True
        verbose_name_plural = "Tracking Data"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.data_type = TrackingDataType.TRACKING.value
        super().save(*args, **kwargs)


class NotificationData(TrackingRequestData):
    objects = NotificationDataManager()

    class Meta(TypedModelMeta):
        proxy = True
        verbose_name_plural = "Notification Data"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.data_type = TrackingDataType.NOTIFICATION.value
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.tracking} @ {self.server_timestamp.strftime("%Y-%m-%d %H:%M:%S")}'


class InterceptionData(TrackingRequestData):
    objects = InterceptionDataManager()

    def __str__(self) -> str:
        return ""

    class Meta(TypedModelMeta):
        proxy = True
        verbose_name_plural = "Interception Data"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.data_type = TrackingDataType.INTERCEPTION.value
        super().save(*args, **kwargs)


#############################
#  Image Tracking Managers  #
#############################


class ImagenDataManager(Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(data_type=ImageDataType.TRACKING.value)


class ExifDataManager(Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(data_type=ImageDataType.REVIEW.value)


##########################
# Image Tracking Models  #
##########################


class ImageRequestData(AbstractRequestData):

    RELATED_NAME = "image_request_data"

    data_type: models.CharField[str, str] = models.CharField(
        max_length=20, choices=ImageDataType.choices(), db_index=True
    )

    tracking: models.ForeignKey[Tracking, Tracking] = models.ForeignKey(
        Tracking, related_name=RELATED_NAME, on_delete=models.CASCADE
    )

    token: models.ForeignKey[Token, Token] = models.ForeignKey(
        Token, related_name=RELATED_NAME, on_delete=models.CASCADE
    )

    # Image file
    image = models.ImageField(
        upload_to="exif_images/%Y/%m/%d/",
        help_text="Upload an image to extract EXIF data",
        null=True,
        blank=True,
    )

    # GPS Coordinates (altitude is EXIF-specific, latitude/longitude inherited from AbstractRequestData)
    altitude: models.FloatField[Optional[float], Optional[float]] = models.FloatField(
        null=True, blank=True, help_text="Altitude from EXIF GPS data (in meters)"
    )

    # Camera/Device Information
    make: models.CharField[str, Optional[str]] = models.CharField(
        max_length=255, blank=True, null=True, help_text="Camera/device manufacturer"
    )

    model: models.CharField[str, Optional[str]] = models.CharField(
        max_length=255, blank=True, null=True, help_text="Camera/device model"
    )

    software: models.CharField[str, Optional[str]] = models.CharField(
        max_length=255, blank=True, null=True, help_text="Software used to create/edit image"
    )

    # Image Properties
    width: models.IntegerField[Optional[int], Optional[int]] = models.IntegerField(
        null=True, blank=True, help_text="Image width in pixels"
    )

    height: models.IntegerField[Optional[int], Optional[int]] = models.IntegerField(
        null=True, blank=True, help_text="Image height in pixels"
    )

    orientation: models.IntegerField[Optional[int], Optional[int]] = models.IntegerField(
        null=True, blank=True, help_text="Image orientation (1-8)"
    )

    # Timestamps
    datetime_original: models.DateTimeField[
        Optional[datetime.datetime], Optional[datetime.datetime]
    ] = models.DateTimeField(
        null=True, blank=True, help_text="Date and time when image was taken (from EXIF)"
    )

    datetime_digitized: models.DateTimeField[
        Optional[datetime.datetime], Optional[datetime.datetime]
    ] = models.DateTimeField(
        null=True, blank=True, help_text="Date and time when image was digitized (from EXIF)"
    )

    # Camera Settings
    exposure_time: models.CharField[str, Optional[str]] = models.CharField(
        max_length=50, blank=True, null=True, help_text="Exposure time (e.g., '1/125')"
    )

    f_number: models.FloatField[Optional[float], Optional[float]] = models.FloatField(
        null=True, blank=True, help_text="F-number (aperture)"
    )

    iso_speed: models.IntegerField[Optional[int], Optional[int]] = models.IntegerField(
        null=True, blank=True, help_text="ISO speed rating"
    )

    focal_length: models.FloatField[Optional[float], Optional[float]] = models.FloatField(
        null=True, blank=True, help_text="Focal length (in mm)"
    )

    flash: models.BooleanField[Optional[bool], Optional[bool]] = models.BooleanField(
        null=True, blank=True, help_text="Flash fired"
    )

    # Raw EXIF data stored as JSON for any additional fields
    raw_exif_data: models.JSONField[Optional[dict[str, Any]], Optional[dict[str, Any]]] = (
        models.JSONField(null=True, blank=True, help_text="Complete raw EXIF data as JSON")
    )

    # Metadata
    created_on: models.DateTimeField[datetime.datetime, datetime.datetime] = models.DateTimeField(
        auto_now_add=True
    )

    updated_on: models.DateTimeField[datetime.datetime, datetime.datetime] = models.DateTimeField(
        auto_now=True
    )

    objects: Manager["ImageRequestData"] = Manager["ImageRequestData"]()

    class Meta(TypedModelMeta):
        verbose_name_plural = "Image Request Data"
        indexes = [
            models.Index(fields=["data_type", "tracking"]),
            models.Index(fields=["data_type", "token"]),
        ]

    def __str__(self) -> str:
        return ""


class ImageData(ImageRequestData):
    objects = ImagenDataManager()

    class Meta(TypedModelMeta):
        proxy = True
        verbose_name_plural = "Image Data"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.data_type = ImageDataType.TRACKING.value
        super().save(*args, **kwargs)


class ExifData(ImageRequestData):
    """Proxy model for EXIF data (REVIEW type)."""

    objects = ExifDataManager()

    class Meta(TypedModelMeta):
        proxy = True
        verbose_name_plural = "EXIF Data"
        ordering = ["-created_on"]

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.data_type = ImageDataType.REVIEW.value
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.make and self.model:
            return f"{self.make} {self.model} - {self.created_on.strftime('%Y-%m-%d %H:%M:%S')}"
        return f"EXIF Data - {self.created_on.strftime('%Y-%m-%d %H:%M:%S')}"
