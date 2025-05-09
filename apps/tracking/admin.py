from django.contrib import admin
from typing import Optional, Any
from django.utils.html import format_html
from django.http import HttpRequest
from django.urls import reverse
from subadmin import SubAdmin  # type: ignore
from tracking.filters import (
    EmailFilter, 
    FirstNameFilter,
    LastNameFilter, 
    PhoneNumberFilter, 
    TokenFilter
)
from tracking.forms import CampaignAdminForm, AgentAdminForm
from tracking.models import TrackingData, Agent, Campaign, AgentTag
from tagulous import admin as TagulousAdmin # type: ignore
from django.db.models import QuerySet

class TrackingDataInline(admin.TabularInline):  # type: ignore
    model = TrackingData
    extra = 0
    can_delete = False
    show_change_link = False
    fields = (
        'server_timestamp', 
        'http_method',
        'ip_address',
        'ip_source',
        'os',
        'browser',
        'platform',
        'locale',
        'client_time',
        'client_timezone',
        'latitude',
        'longitude',
        'location_source',
        'view_details'
    )
    readonly_fields = fields
    search_fields = ('http_method',)
    list_filter = ('http_method',)
    list_per_page = 20

    def view_details(self, obj: TrackingData) -> str:
        """Display a link to view the details in a modal dialog."""
        url = reverse('tracking_data_dialog', args=[obj.pk])
        return format_html(
            '<a href="{}" class="button" onclick="return showRelatedObjectLookupPopup(this);">View Details</a>',
            f"{url}?_popup=1"
        )
    view_details.short_description = 'Details'  # type: ignore

    def has_add_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).select_related('agent')


class AgentAdmin(SubAdmin, TagulousAdmin.TaggedModelAdmin): # type: ignore
    model = Agent
    form = AgentAdminForm
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'status')}),
        ('Contact', {'fields': ('token', 'email', 'phone_number')}),
        ('Metadata', {'fields': ('tags',)}),
    )
    
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'status', 'get_tags')
    list_filter = (
        FirstNameFilter,
        LastNameFilter,
        EmailFilter,
        PhoneNumberFilter,
        TokenFilter,
        'status',
        'tags'
    )
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'token', 'status', 'tags__name')
    ordering = ('first_name', 'last_name', 'email', 'phone_number', 'status')
    inlines = [TrackingDataInline]

    @admin.display(description='Tags')
    def get_tags(self, obj: Agent) -> str:
        """Return a comma-separated list of tags."""
        agent_tags: QuerySet[AgentTag] = obj.tags.all()  # type: ignore[attr-defined]
        
        return ", ".join(tag.name for tag in agent_tags) if agent_tags else ""


class CampaignAdmin(SubAdmin):
    model = Campaign
    form = CampaignAdminForm
    fieldsets = (
        (None, {'fields': ('name', 'description')}),
        ('Website Details', {'fields': ('publishing_type', 'landing_page_url', 'tracking_pixel')}),
        ('Tracking Configuration', {'fields': (
            ('ip_tracking', 'ip_precedence'),
            ('location_tracking', 'location_precedence'),
            ('locale_tracking', 'locale_precedence'),
            ('browser_tracking', 'browser_precedence'),
            ('time_tracking', 'time_precedence')
        )}),
    )
    subadmins = [AgentAdmin]

TagulousAdmin.enhance(Agent, AgentAdmin) # type: ignore