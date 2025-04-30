from django.contrib import admin
from typing import Optional, Any
from django.utils.html import format_html
# from django.utils.safestring import mark_safe
from django.http import HttpRequest
from django.urls import reverse
from subadmin import SubAdmin  # type: ignore
from tracking.forms import CampaignAdminForm
from tracking.models import TrackingData, Agent, Campaign
from django_json_widget.widgets import JSONEditorWidget # type: ignore


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


class AgentAdmin(SubAdmin):
    model = Agent
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'status')}),
        ('Contact', {'fields': ('token', 'email', 'phone_number')}),
    )
    
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'status')
    list_filter = ('status',)
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    ordering = ('first_name',)
    inlines = [TrackingDataInline]


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
