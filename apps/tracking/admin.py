import json
from django.contrib import admin
from typing import Optional, Any, Dict, List
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpRequest
from subadmin import SubAdmin  # type: ignore
from tracking.forms import CampaignAdminForm
from tracking.models import TrackingData, Agent, Campaign


def parse_json_data(data: Any) -> Dict[str, Any]:
    """Parse JSON data from string or dict."""
    if isinstance(data, str):
        return json.loads(data)
    return data


class TrackingDataInline(admin.TabularInline):  # type: ignore
    model = TrackingData
    extra = 0
    show_change_link = False
    can_delete = False
    fields = (
        'id', 
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
        'warnings',
        'metadata'
    )
    readonly_fields = fields
    search_fields = ('http_method',)
    list_filter = ('http_method',)
    list_per_page = 20

    def has_add_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Optional[Any] = None) -> bool:
        return False

    # def get_queryset(self, request: HttpRequest) -> QuerySet[TrackingData]:
    #     return cast(QuerySet[TrackingData], super().get_queryset(request).order_by('-server_timestamp'))
    
    def check_ip_mismatch(self, obj: TrackingData) -> Optional[str]:
        """Check for IP address mismatches between server and client."""
        if not obj.ip_data:
            return None

        ip_data = parse_json_data(obj.ip_data)
        server_ip = ip_data.get('server_ip', {}).get('address')
        header_ip = ip_data.get('header_ip', {}).get('address')
        
        if server_ip and header_ip and server_ip != header_ip:
            return format_html(
                '<span class="warning-icon" title="IP Address Mismatch: Server IP ({}) differs from Client IP ({})">🌐</span>',
                server_ip,
                header_ip
            )
        return None

    def check_vpn(self, obj: TrackingData) -> Optional[str]:
        """Check for VPN/proxy usage."""
        if not obj.ip_data:
            return None

        ip_data = parse_json_data(obj.ip_data)
        if ip_data.get('info', {}).get('security', {}).get('is_vpn'):
            return format_html(
                '<span class="warning-icon" title="VPN/Proxy Detected">🔒</span>'
            )
        return None

    def check_crawler(self, obj: TrackingData) -> Optional[str]:
        """Check for crawler/bot detection."""
        if not obj.user_agent_data:
            return None

        ua_data = parse_json_data(obj.user_agent_data)
        if ua_data.get('info', {}).get('crawler', {}).get('is_crawler'):
            return format_html(
                '<span class="warning-icon" title="Crawler/Bot Detected">🤖</span>'
            )
        return None

    def check_user_agent_mismatch(self, obj: TrackingData) -> Optional[str]:
        """Check for user agent mismatches."""
        if not obj.user_agent_data:
            return None

        ua_data = parse_json_data(obj.user_agent_data)
        if ua_data.get('server_user_agent') != ua_data.get('header_user_agent'):
            return format_html(
                '<span class="warning-icon" title="User Agent Mismatch: Server and Client user agents differ">🔄</span>'
            )
        return None

    def check_timezone_mismatch(self, obj: TrackingData) -> Optional[str]:
        """Check for timezone mismatches."""
        if not obj.headers_data or not obj.ip_data:
            return None

        header_timezone: Optional[str] = obj.headers_data.get('datetime', {}).get('timezone') if obj.headers_data else None
        ip_timezone: Optional[str] = obj.ip_data.get('info', {}).get('timezone', {}).get('name') if obj.ip_data else None

        if header_timezone != ip_timezone:
            return format_html(
                '<span class="warning-icon" title="Non-UTC Timezone: {}">⏰</span>',
                obj.client_timezone
            )
        return None

    def check_security(self, obj: TrackingData) -> Optional[str]:
        """Check for security issues."""
        if not obj.ip_data:
            return None
        
        ip_data = parse_json_data(obj.ip_data)
        security = ip_data.get('info', {}).get('security', {})
        
        warnings: List[str] = []
        for key, label in {
            'vpn': 'VPN',
            'proxy': 'Proxy',
            'tor': 'Tor',
            'relay': 'Relay',
            'hosting': 'Hosting'
        }.items():
            if security.get(key):
                warnings.append(label)
        
        if warnings:
            return format_html(
                '<span class="warning-icon" title="Security Issues: {}">🔒</span>',
                ', '.join(warnings)
            )
        return None

    def warnings(self, obj: TrackingData) -> str:
        """Collect all warnings for the tracking data."""
        warning_checks = [
            self.check_ip_mismatch,
            self.check_vpn,
            self.check_security,
            self.check_crawler,
            self.check_user_agent_mismatch,
            self.check_timezone_mismatch
        ]
        
        warnings: List[str] = []
        for check in warning_checks:
            if warning := check(obj):
                warnings.append(warning)
        
        return mark_safe(' '.join(warnings)) if warnings else '-'
    
    warnings.short_description = 'Warnings'  # type: ignore

    def metadata(self, obj: TrackingData) -> str:
        """Display metadata icons with tooltips."""
        metadata_fields = {
            'headers_data': ('📋', 'Headers Data'),
            'ip_data': ('🌐', 'IP Data'),
            'user_agent_data': ('🖥️', 'User Agent Data'),
            'form_data': ('📝', 'Form Data')
        }
        
        icons: List[str] = []
        for field, (icon, _) in metadata_fields.items():
            if data := getattr(obj, field):
                icons.append(format_html(
                    '<span class="metadata-icon" title="{}">{}</span>',
                    json.dumps(parse_json_data(data), indent=4, ensure_ascii=False),
                    icon
                ))
        
        return mark_safe(' '.join(icons))
    
    metadata.short_description = 'Metadata'  # type: ignore
    
    class Media:
        css = {
            'all': (
                '.metadata-icon { margin-right: 5px; }',
                '.metadata-icon:hover { cursor: pointer; opacity: 0.7; }',
                '.warning-icon { margin-right: 5px; color: #ff9800; }',
                '.warning-icon:hover { cursor: pointer; opacity: 0.7; }',
            )
        }


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
