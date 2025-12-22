from typing import Any
from typing import Optional
from common.enums import CampaignDataType
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString
from subadmin import SubAdmin
from tracking.filters import BaseTextFieldFilter
from tracking.filters import process_list_filter
from tracking.forms import CampaignSubAdminForm
from tracking.forms import RecipientSubAdminForm
from tracking.forms import TrackingSubAdminForm

# from tracking.models import ExifData
# from tracking.models import TrackingData
from tracking.models import AbstractRequestData
from tracking.models import Campaign
from tracking.models import ImageRequestData
from tracking.models import Recipient
from tracking.models import Token
from tracking.models import Tracking
from tracking.models import TrackingRequestData


class TokenInline(admin.TabularInline[Token, Tracking]):
    model = Token
    extra = 0
    fields = ("value", "status", "created_on", "last_used", "used", "deleted_on")
    readonly_fields = ("created_on", "last_used", "used", "deleted_on")
    ordering = ("-last_used", "-created_on")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Token]:
        return super().get_queryset(request).select_related("tracking")

    @admin.display(description="Used")
    def used(self, obj: Token) -> int | str:
        return obj.tracking.count_requests or "-"


class AbstractTrackingDataInline(admin.TabularInline[AbstractRequestData, Tracking]):
    """Inline for displaying TrackingRequestData (for PACKAGES campaigns)."""

    model = AbstractRequestData
    extra = 0
    can_delete = False
    show_change_link = False
    fields = (
        "timestamp",
        "data_type",
        "http_method",
        "ip_address",
        "os",
        "browser",
        "platform",
        "locale",
        "client_time",
        "client_timezone",
        "latitude",
        "longitude",
    )
    readonly_fields = fields
    search_fields = ("http_method",)
    list_filter = ("http_method",)
    list_per_page = 20

    def has_add_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False

    @admin.display(description="Timestamp")
    def timestamp(self, obj: AbstractRequestData) -> str:
        return format_html(
            '<a href="{}" class="button">{}</a>',
            f"{reverse('tracking_data_dialog', args=[obj.tracking.campaign.campaign_type, obj.pk])}?_popup=1",
            obj.server_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[AbstractRequestData]:
        return super().get_queryset(request).select_related("tracking", "token")


class TrackingDataInline(AbstractTrackingDataInline):
    model = TrackingRequestData

    # def get_queryset(self, request: HttpRequest) -> QuerySet[AbstractRequestData]:
    #     return super().get_queryset(request).select_related("tracking", "token")


class ExifDataInline(AbstractTrackingDataInline):
    model = ImageRequestData

    # def get_queryset(self, request: HttpRequest) -> QuerySet[AbstractRequestData]:
    #     return super().get_queryset(request).select_related("tracking", "token")


class TrackingSubAdmin(SubAdmin[Tracking]):
    model = Tracking
    form = TrackingSubAdminForm
    extra = 1

    def get_readonly_fields(
        self, request: HttpRequest, obj: Optional[Tracking] = None
    ) -> tuple[str, ...]:
        """Make recipient and campaign readonly when editing existing objects."""
        if obj:  # Editing an existing object
            return ("recipient", "campaign")
        return ()  # Creating a new object - fields are editable

    list_display = (
        "id",
        "campaign_name",
        "recipient_name",
        "recipient_email",
        "recipient_phone",
        "recipient_status",
    )
    list_filter = process_list_filter(
        (
            "recipient__status",
            ("tokens__value", BaseTextFieldFilter),
            ("recipient__first_name", BaseTextFieldFilter),
            ("recipient__last_name", BaseTextFieldFilter),
            ("recipient__email", BaseTextFieldFilter),
            ("recipient__phone_number", BaseTextFieldFilter),
            ("campaign__name", BaseTextFieldFilter),
        )
    )
    search_fields = (
        "tokens__value",
        "recipient__first_name",
        "recipient__last_name",
        "recipient__email",
        "recipient__phone_number",
        "campaign__name",
    )
    list_per_page = 20
    show_change_link = True
    # Default inlines - will be overridden by get_inlines based on campaign type

    def get_inlines(
        self, request: HttpRequest, obj: Optional[Tracking]
    ) -> tuple[type[admin.TabularInline[Any, Any]], ...]:

        campaign = obj.campaign if obj else None

        if campaign and campaign.campaign_type == CampaignDataType.IMAGES.value:
            return (TokenInline, ExifDataInline)
        elif campaign and campaign.campaign_type == CampaignDataType.PACKAGES.value:
            return (TokenInline, TrackingDataInline)

        return (TokenInline,)

    @admin.display(description="Recipient")
    def recipient_name(self, obj: Tracking) -> SafeString:
        """Display recipient full name as a link."""
        if not obj.recipient or not obj.company:
            return format_html("-")
        name = f'{obj.recipient.first_name or ""} {obj.recipient.last_name or ""}'.strip()
        if not name:
            name = f"Recipient #{obj.recipient.id}"
        # Construct URL using SubAdmin nested pattern
        # Recipient is a subadmin of Company, so URL is: mgmt_company_recipient_change
        try:
            url = reverse(
                "admin:mgmt_company_recipient_change",
                args=[obj.company.pk, obj.recipient.pk],
            )
        except Exception:
            # Fallback if URL pattern doesn't exist
            url = f"/admin/mgmt/company/{obj.company.pk}/recipient/{obj.recipient.pk}/change/"
        return format_html('<a href="{}">{}</a>', url, name)

    @admin.display(description="Email")
    def recipient_email(self, obj: Tracking) -> str:
        """Display recipient email."""
        return obj.recipient.email if obj.recipient and obj.recipient.email else "-"

    @admin.display(description="Phone")
    def recipient_phone(self, obj: Tracking) -> str:
        """Display recipient phone number."""
        return obj.recipient.phone_number if obj.recipient and obj.recipient.phone_number else "-"

    @admin.display(description="Status")
    def recipient_status(self, obj: Tracking) -> str:
        """Display recipient status."""
        return obj.recipient.status if obj.recipient else "-"

    @admin.display(description="Campaign")
    def campaign_name(self, obj: Tracking) -> SafeString:
        """Display campaign name as a link."""
        if not obj.campaign or not obj.company:
            return format_html("-")
        # Construct URL using SubAdmin nested pattern
        # Campaign is a subadmin of Company, so URL is: mgmt_company_campaign_change
        try:
            url = reverse(
                "admin:mgmt_company_campaign_change",
                args=[obj.company.pk, obj.campaign.pk],
            )
        except Exception:
            # Fallback if URL pattern doesn't exist
            url = f"/admin/mgmt/company/{obj.company.pk}/campaign/{obj.campaign.pk}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.campaign.name)

    @admin.display(description="Token")
    def token_value(self, obj: Tracking) -> str:
        """Display token values (comma-separated if multiple)."""
        tokens = obj.tokens.all()
        if not tokens.exists():
            return "-"
        return ", ".join(token.value for token in tokens)


class RecipientSubAdmin(SubAdmin[Recipient]):
    model = Recipient
    form = RecipientSubAdminForm
    fieldsets = (
        (None, {"fields": ("first_name", "last_name", "status")}),
        ("Contact", {"fields": ("email", "phone_number")}),
        ("Metadata", {"fields": ("tags",)}),
    )
    list_display = ("first_name", "last_name", "email", "phone_number", "status", "display_tags")
    list_filter = process_list_filter(
        (
            ("first_name", BaseTextFieldFilter),
            ("last_name", BaseTextFieldFilter),
            ("email", BaseTextFieldFilter),
            ("phone_number", BaseTextFieldFilter),
            ("tags__name", BaseTextFieldFilter),
            "status",
        )
    )
    search_fields = (
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "status",
        "tags__name",
    )
    ordering = ("first_name", "last_name", "email", "phone_number", "status")

    @admin.display(description="Tags")
    def display_tags(self, obj: Recipient) -> SafeString:
        """Display tags with color coding based on status"""
        if not obj.tags.exists():
            return format_html("-")

        tags_html = []
        for tag in obj.tags.all():
            tags_html.append(format_html('<span style="color: grey">{}</span>', tag.name))

        return format_html(", ".join(tags_html))


class CampaignSubAdmin(SubAdmin[Campaign]):
    model = Campaign
    form = CampaignSubAdminForm
    fieldsets = (
        (None, {"fields": ("campaign_type", "name", "description")}),
        ("Website Details", {"fields": ("publishing_type", "landing_page_url", "tracking_pixel")}),
        (
            "Tracking Configuration",
            {
                "fields": (
                    ("ip_tracking", "ip_precedence"),
                    ("location_tracking", "location_precedence"),
                    ("locale_tracking", "locale_precedence"),
                    ("browser_tracking", "browser_precedence"),
                    ("time_tracking", "time_precedence"),
                )
            },
        ),
    )
    ordering = ("name",)
