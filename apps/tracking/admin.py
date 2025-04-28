from django.contrib import admin
from typing import Optional, Any, List, Dict
from django.utils.html import format_html
# from django.utils.safestring import mark_safe
from django.http import HttpRequest
from django.urls import reverse
from subadmin import SubAdmin  # type: ignore
from tracking.forms import CampaignAdminForm
from tracking.models import TrackingData, Agent, Campaign
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget # type: ignore

@admin.register(TrackingData)
class TrackingDataAdmin(admin.ModelAdmin):  # type: ignore
    model = TrackingData
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'server_timestamp',
                'http_method',
                'ip_address',
                'ip_source',
            ),
            'classes': ('collapse',)
        }),
        ('Client Information', {
            'fields': (
                'os',
                'browser',
                'platform',
                'locale',
                'client_time',
                'client_timezone',
            ),
            'classes': ('collapse',)
        }),
        ('Location Information', {
            'fields': (
                'latitude',
                'longitude',
                'location_source',
            ),
            'classes': ('collapse',)
        }),
        ('Data Fields', {
            'fields': (
                'ip_data',
                'user_agent_data',
                'header_data',
                'form_data'
            ),
            'classes': ('collapse',)
        }),
        ('Security Checks', {
            'fields': (
                'ip_mismatch',
                'country_mismatch',
                'user_agent_mismatch',
                'timezone_mismatch',
                'locale_mismatch',
                'security_issues',
                'crawler_detection',
            ),
            'classes': ('collapse',)
        })
    )
    readonly_fields = (
        'server_timestamp', 'http_method', 'ip_address', 'ip_source',
        'os', 'browser', 'platform', 'locale', 'client_time', 'client_timezone',
        'latitude', 'longitude', 'location_source',
        '_ip_data', '_user_agent_data', '_header_data', '_form_data',
        'ip_mismatch', 'country_mismatch', 'user_agent_mismatch',
        'timezone_mismatch', 'locale_mismatch', 'security_issues',
        'crawler_detection'
    )
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }

    def has_add_permission(self, request: HttpRequest, obj: Optional[TrackingData] = None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Optional[TrackingData] = None) -> bool:
        return False
    
    def has_list_view(self, request: HttpRequest, obj: Optional[TrackingData] = None) -> bool:
        return False

    def ip_mismatch(self, obj: TrackingData) -> str:
        """Check for IP address mismatches between server and client."""
        ip_data = obj.ip_data
        
        if not ip_data:
            return 'No IP data available'

        server_ip = ip_data.getServerIpAddress()
        header_ip = ip_data.getHeaderIpAddress()
        
        if server_ip and header_ip and server_ip != header_ip:
            return format_html(
                '<span style="color: #ff9800;">⚠️ IP Address Mismatch: Server IP ({}) differs from Header IP ({})</span>',
                server_ip,
                header_ip
            )
        return '✅ IP addresses match'

    def country_mismatch(self, obj: TrackingData) -> str:
        """Check for country mismatches between server and client."""
        ip_data = obj.ip_data
        header_data = obj.header_data 

        if not ip_data or not header_data:
            return 'No data available for comparison'

        server_country = ip_data.getSelectedCountry()
        header_country = header_data.getHeaderCountry()
        
        if server_country and header_country and server_country != header_country:
            return format_html(
                '<span style="color: #ff9800;">⚠️ Country Mismatch: Server country ({}) differs from Header country ({})</span>',
                server_country,
                header_country
            )
        return '✅ Countries match'

    def crawler_detection(self, obj: TrackingData) -> str:
        """Check for crawler/bot detection."""
        user_agent_data = obj.user_agent_data

        if not user_agent_data:
            return 'No user agent data available'

        if user_agent_data.is_crawler():
            return format_html(
                '<span style="color: #ff9800;">⚠️ Crawler/Bot Detected</span>'
            )
        return '✅ No crawler detected'

    def user_agent_mismatch(self, obj: TrackingData) -> str:
        """Check for user agent mismatches."""
        user_agent_data = obj.user_agent_data

        if not user_agent_data:
            return 'No user agent data available'

        if user_agent_data.header != user_agent_data.server:
            return format_html(
                '<span style="color: #ff9800;">⚠️ User Agent Mismatch: Server and Client user agents differ</span>'
            )
        return '✅ User agents match'

    def timezone_mismatch(self, obj: TrackingData) -> str:
        """Check for timezone mismatches."""
        ip_data = obj.ip_data
        header_data = obj.header_data 

        if not ip_data or not header_data:
            return 'No data available for comparison'

        header_timezone = header_data.getTimezone()
        ip_timezone = ip_data.getTimezone()

        if header_timezone != ip_timezone:
            return format_html(
                '<span style="color: #ff9800;">⚠️ Timezone Mismatch: Header timezone ({}) differs from IP timezone ({})</span>',
                header_timezone,
                ip_timezone
            )
        return '✅ Timezones match'

    def locale_mismatch(self, obj: TrackingData) -> str:
        """Check for locale mismatches between server and client."""
        ip_data = obj.ip_data
        header_data = obj.header_data 

        if not ip_data or not header_data:
            return 'No data available for comparison'
        
        server_locale = ip_data.getLocales()
        header_locale = header_data.getLocale()
        
        if server_locale and header_locale and server_locale[0] != header_locale:
            return format_html(
                '<span style="color: #ff9800;">⚠️ Locale Mismatch: Server locale ({}) differs from Browser locale ({})</span>',
                server_locale[0],
                header_locale
            )
        return '✅ Locales match'

    def security_issues(self, obj: TrackingData) -> str:
        """Check for security issues."""
        ip_data = obj.ip_data
        if not ip_data:
            return 'No IP data available'

        warnings: List[str] = []
        security: Dict[str, bool] = {
            'vpn': ip_data.isVpn(),
            'proxy': ip_data.isProxy(),
            'tor': ip_data.isTor(),
            'relay': ip_data.isRelay()
        }
        for key, label in security.items():
            if label:
                warnings.append(format_html('<span style="color: #ff9800;">⚠️ {} detected</span>', key.title()))
        
        if warnings:
            return format_html('<br>'.join(warnings))
        return '✅ No security issues detected'


class TrackingDataInline(admin.TabularInline):  # type: ignore
    model = TrackingData
    extra = 0
    can_delete = False
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
        """Display a link to view the details in a modal."""
        url = reverse('admin:tracking_trackingdata_change', args=[obj.pk])
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
