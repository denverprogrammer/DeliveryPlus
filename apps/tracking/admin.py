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
    extra = 0
    show_change_link = False
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
        '_ip_data',
        '_user_agent_data',
        '_header_data',
        '_form_data'
    )
    readonly_fields = fields
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }

    def has_add_permission(self, request: HttpRequest, obj: Optional[TrackingData] = None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Optional[TrackingData] = None) -> bool:
        return False
    
    def has_list_view(self, request: HttpRequest, obj: Optional[TrackingData] = None) -> bool:
        return False

    def check_ip_mismatch(self, obj: TrackingData) -> Optional[str]:
        """Check for IP address mismatches between server and client."""
        ip_data = obj.ip_data
        
        if not ip_data:
            return None

        server_ip = ip_data.getServerIpAddress()
        header_ip = ip_data.getHeaderIpAddress()
        
        if server_ip and header_ip and server_ip != header_ip:
            return format_html(
                '<span>IP Address Mismatch: Server IP ({}) differs from Header IP ({})</span>',
                server_ip,
                header_ip
            )
        return None

    def check_country_mismatch(self, obj: TrackingData) -> Optional[str]:
        """Check for country mismatches between server and client."""
        ip_data = obj.ip_data
        header_data = obj.header_data 

        if not ip_data or not header_data:
            return None

        server_country = ip_data.getSelectedCountry()
        header_country = header_data.getHeaderCountry()
        
        if server_country and header_country and server_country != header_country:
            return format_html(
                '<span>Country Mismatch: Server country ({}) differs from Header country ({})</span>',
                server_country,
                header_country
            )
        return None

    def check_crawler(self, obj: TrackingData) -> Optional[str]:
        """Check for crawler/bot detection."""
        user_agent_data = obj.user_agent_data

        if not user_agent_data:
            return None

        if user_agent_data.is_crawler():
            return format_html(
                '<span>Crawler/Bot Detected</span>'
            )
        return None

    def check_user_agent_mismatch(self, obj: TrackingData) -> Optional[str]:
        """Check for user agent mismatches."""
        user_agent_data = obj.user_agent_data

        if not user_agent_data:
            return None

        if user_agent_data.header != user_agent_data.server:
            return format_html(
                '<span>User Agent Mismatch: Server and Client user agents differ</span>'
            )
        return None

    def check_timezone_mismatch(self, obj: TrackingData) -> Optional[str]:
        """Check for timezone mismatches."""
        ip_data = obj.ip_data
        header_data = obj.header_data 

        if not ip_data or not header_data:
            return None

        header_timezone = header_data.getTimezone()
        ip_timezone = ip_data.getTimezone()

        if header_timezone != ip_timezone:
            return format_html(
                '<span>Timezone Mismatch: Header timezone ({}) differs from IP timezone ({})</span>',
                header_timezone,
                ip_timezone
            )
        return None

    def check_locale_mismatch(self, obj: TrackingData) -> Optional[str]:
        """Check for locale mismatches between server and client."""
        ip_data = obj.ip_data
        header_data = obj.header_data 

        if not ip_data or not header_data:
            return None
        
        server_locale = ip_data.getLocales()
        header_locale = header_data.getLocale()
        
        if server_locale and header_locale and server_locale[0] != header_locale:
            return format_html(
                '<span>Locale Mismatch: Server locale ({}) differs from Browser locale ({})</span>',
                server_locale[0],
                header_locale
            )
        return None

    def check_security(self, obj: TrackingData) -> Optional[List[str]]:
        """Check for security issues."""
        ip_data = obj.ip_data
        if not ip_data:
            return None

        warnings: List[str] = []
        security: Dict[str, bool] = {
            'vpn': ip_data.isVpn(),
            'proxy': ip_data.isProxy(),
            'tor': ip_data.isTor(),
            'relay': ip_data.isRelay()
        }
        for key, label in security.items():
            if label:
                warnings.append(format_html('<span>{} detected</span>', key.title()))
        
        return warnings if warnings else None

    def details(self, obj: TrackingData) -> str:
        """Display warnings and metadata."""
        # Render the modal template
        # checks: List[str|None] = [
        #     self.check_ip_mismatch(obj),
        #     self.check_country_mismatch(obj),
        #     self.check_locale_mismatch(obj),
        #     self.check_crawler(obj),
        #     self.check_user_agent_mismatch(obj),
        #     self.check_timezone_mismatch(obj)
        # ]
        # security: Optional[List[str]] = self.check_security(obj)
        # if security:
        #     checks.extend(security)
        # warnings = [warning for warning in checks if warning]
        return ''


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
        url = f"{url}?_popup=1"
        return format_html('<a href="{}">View Details</a>', url)
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
