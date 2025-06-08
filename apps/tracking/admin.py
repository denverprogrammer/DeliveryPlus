from typing import Any
from typing import Optional
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from subadmin import SubAdmin
from tagulous import admin as TagulousAdmin
from tracking.filters import EmailFilter
from tracking.filters import FirstNameFilter
from tracking.filters import LastNameFilter
from tracking.filters import PhoneNumberFilter
from tracking.filters import TokenFilter
from tracking.forms import AgentAdminForm
from tracking.forms import CampaignAdminForm
from tracking.models import Agent
from tracking.models import AgentTag
from tracking.models import Campaign
from tracking.models import TrackingData


class TrackingDataInline(admin.TabularInline[TrackingData, Agent]):
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

    @admin.display(description="Details")
    def view_details(self, obj: Agent) -> str:
        """Return a comma-separated list of tags."""
        url = reverse("tracking_data_dialog", args=[obj.pk])
        return format_html(
            '<a href="{}" class="button" onclick="{}">View Details</a>',
            f"{url}?_popup=1",
            "return showRelatedObjectLookupPopup(this);",
        )

    def has_add_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet[TrackingData]:
        return super().get_queryset(request).select_related("agent")


# TODO: SubAdmin when to version that allows Django 5.2
class AgentAdmin(TagulousAdmin.TaggedModelAdmin, SubAdmin[Agent]):
    model = Agent
    form = AgentAdminForm
    fieldsets = (
        (None, {"fields": ("first_name", "last_name", "status")}),
        ("Contact", {"fields": ("token", "email", "phone_number")}),
        ("Metadata", {"fields": ("tags",)}),
    )

    list_display = ("first_name", "last_name", "email", "phone_number", "status", "get_tags")
    list_filter = (
        FirstNameFilter,
        LastNameFilter,
        EmailFilter,
        PhoneNumberFilter,
        TokenFilter,
        "status",
        "tags",
    )
    search_fields = (
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "token",
        "status",
        "tags__name",
    )
    ordering = ("first_name", "last_name", "email", "phone_number", "status")
    inlines = (TrackingDataInline,)

    @admin.display(description="Tags")
    def get_tags(self, obj: Agent) -> str:
        """Return a comma-separated list of tags."""
        agent_tags: QuerySet[AgentTag] = obj.tags.all()

        return ", ".join(tag.name for tag in agent_tags) if agent_tags else ""


class CampaignAdmin(SubAdmin[Campaign]):
    model = Campaign
    form = CampaignAdminForm
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
    subadmins = [AgentAdmin]


TagulousAdmin.enhance(Agent, AgentAdmin)
