from typing import Any
from typing import Optional
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString
from subadmin import SubAdmin
from tracking.filters import RecipientEmailFilter
from tracking.filters import RecipientFirstNameFilter
from tracking.filters import RecipientLastNameFilter
from tracking.filters import RecipientPhoneNumberFilter
from tracking.filters import RecipientTagsFilter
from tracking.filters import TrackingCampaignNameFilter
from tracking.filters import TrackingEmailFilter
from tracking.filters import TrackingFirstNameFilter
from tracking.filters import TrackingLastNameFilter
from tracking.filters import TrackingPhoneNumberFilter
from tracking.filters import TrackingTokenFilter
from tracking.forms import CampaignSubAdminForm
from tracking.forms import RecipientSubAdminForm
from tracking.forms import TrackingSubAdminForm
from tracking.models import Campaign
from tracking.models import Recipient
from tracking.models import Tracking
from tracking.models import TrackingData


class TrackingDataInline(admin.TabularInline[TrackingData, Tracking]):
    model = TrackingData
    extra = 0
    can_delete = False
    show_change_link = False
    fields = (
        "server_timestamp",
        "http_method",
        "ip_address",
        "ip_source",
        "os",
        "browser",
        "platform",
        "locale",
        "client_time",
        "client_timezone",
        "latitude",
        "longitude",
        "location_source",
        "view_details",
    )
    readonly_fields = fields
    search_fields = ("http_method",)
    list_filter = ("http_method",)
    list_per_page = 20

    def has_add_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False

    @admin.display(description="Details")
    def view_details(self, obj: Tracking) -> str:
        """Return a comma-separated list of tags."""
        url = reverse("tracking_data_dialog", args=[obj.pk])
        return format_html(
            '<a href="{}" class="button" onclick="{}">View Details</a>',
            f"{url}?_popup=1",
            "return showRelatedObjectLookupPopup(this);",
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[TrackingData]:
        return super().get_queryset(request).select_related("tracking")


class TrackingSubAdmin(SubAdmin[Tracking]):
    model = Tracking
    form = TrackingSubAdminForm
    extra = 1
    list_display = (
        "id",
        "recipient_name",
        "recipient_email",
        "recipient_phone",
        "recipient_status",
        "campaign_name",
        "token",
    )
    list_filter = (
        "recipient__status",
        TrackingTokenFilter,
        TrackingFirstNameFilter,
        TrackingLastNameFilter,
        TrackingEmailFilter,
        TrackingPhoneNumberFilter,
        TrackingCampaignNameFilter,
    )
    search_fields = (
        "token",
        "recipient__first_name",
        "recipient__last_name",
        "recipient__email",
        "recipient__phone_number",
        "campaign__name",
    )
    list_per_page = 20
    show_change_link = True
    inlines = (TrackingDataInline,)

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


class RecipientSubAdmin(SubAdmin[Recipient]):
    model = Recipient
    form = RecipientSubAdminForm
    fieldsets = (
        (None, {"fields": ("first_name", "last_name", "status")}),
        ("Contact", {"fields": ("email", "phone_number")}),
        ("Metadata", {"fields": ("tags",)}),
    )
    list_display = ("first_name", "last_name", "email", "phone_number", "status", "display_tags")
    list_filter = (
        RecipientFirstNameFilter,
        RecipientLastNameFilter,
        RecipientEmailFilter,
        RecipientPhoneNumberFilter,
        RecipientTagsFilter,
        "status",
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
    # inlines = (RecipientTrackingInline,)

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
        (None, {"fields": ("name", "description")}),
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
    # inlines = (CampaignTrackingInline,)
