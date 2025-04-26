import json
from django.contrib import admin
from typing import Optional, Any, List, TypeVar
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpRequest
from django.template.loader import render_to_string
from subadmin import SubAdmin  # type: ignore
from config.common import HeaderData
from tracking.api.types import IpData, UserAgentData
from tracking.forms import CampaignAdminForm
from tracking.models import TrackingData, Agent, Campaign
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

def parse_json_data(data: Any, model: type[T]) -> T:
    """Parse JSON data from string or dict into a Pydantic model."""
    if isinstance(data, str):
        return model.model_validate_json(data)
    return model.model_validate(data)


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
        
        _ip_data = getattr(obj, '_ip_data', None)

        if not _ip_data:
            _ip_data = parse_json_data(obj.ip_data, IpData)
            setattr(obj, '_ip_data', _ip_data)
        
        server_ip = _ip_data.getServerIpAddress()
        header_ip = _ip_data.getHeaderIpAddress()
        
        if server_ip != header_ip:
            return format_html(
                '<span class="warning-icon" title="IP Address Mismatch: Server IP ({}) differs from Client IP ({})">🌐</span>',
                server_ip,
                header_ip
            )
        return None

    def check_crawler(self, obj: TrackingData) -> Optional[str]:
        """Check for crawler/bot detection."""
        if not obj.user_agent_data:
            return None
        
        _user_agent_data = getattr(obj, '_user_agent_data', None)

        if not _user_agent_data:
            _user_agent_data = parse_json_data(obj.user_agent_data, UserAgentData)
            setattr(obj, '_user_agent_data', _user_agent_data)

        if _user_agent_data.is_crawler():
            return format_html(
                '<span class="warning-icon" title="Crawler/Bot Detected">🤖</span>'
            )
        return None

    def check_user_agent_mismatch(self, obj: TrackingData) -> Optional[str]:
        """Check for user agent mismatches."""
        if not obj.user_agent_data:
            return None
        
        _user_agent_data = getattr(obj, '_user_agent_data', None)

        if not _user_agent_data:
            _user_agent_data = parse_json_data(obj.user_agent_data, UserAgentData)
            setattr(obj, '_user_agent_data', _user_agent_data)

        if _user_agent_data.header != _user_agent_data.server:
            return format_html(
                '<span class="warning-icon" title="User Agent Mismatch: Server and Client user agents differ">🔄</span>'
            )
        return None

    def check_timezone_mismatch(self, obj: TrackingData) -> Optional[str]:
        """Check for timezone mismatches."""
        if not obj.ip_data and obj.headers_data:
            return None
        
        _ip_data = getattr(obj, '_ip_data', None)
        _headers_data = getattr(obj, '_headers_data', None)

        if not _ip_data or not _headers_data:
            _ip_data = parse_json_data(obj.ip_data, IpData)
            _headers_data = parse_json_data(obj.headers_data, HeaderData)
            setattr(obj, '_ip_data', _ip_data)
            setattr(obj, '_headers_data', _headers_data)
        header_timezone: Optional[str] = _headers_data.getTimezone()
        ip_timezone: Optional[str] = _ip_data.getTimezone()

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
        _ip_data = getattr(obj, '_ip_data', None)

        if not _ip_data:
            _ip_data = parse_json_data(obj.ip_data, IpData)
            setattr(obj, '_ip_data', _ip_data)

        warnings: List[str] = []
        for key, label in {
            'vpn': _ip_data.isVpn(),
            'proxy': _ip_data.isProxy(),
            'tor': _ip_data.isTor(),
            'relay': _ip_data.isRelay()
        }.items():
            if label:
                warnings.append(f'<span class="warning-icon" title="{ key } detected">🔒</span>')
        
        if warnings:
            return format_html( '{}', ', '.join(warnings))
        return None

    def metadata(self, obj: TrackingData) -> str:
        """Display metadata icons with tooltips."""       
        # Render the modal template

        warning_checks = [
            self.check_ip_mismatch,
            self.check_security,
            self.check_crawler,
            self.check_user_agent_mismatch,
            self.check_timezone_mismatch
        ]
        
        warnings: List[str] = []
        for check in warning_checks:
            if warning := check(obj):
                warnings.append(warning)

        modal_html = render_to_string(
            'admin/tracking/trackingdata/metadata_modal.html',
            {
                'obj': obj,
                'headers_data': json.loads(obj.headers_data) if obj.headers_data else None,
                'ip_data': json.loads(obj.ip_data) if obj.ip_data else None,
                'user_agent_data': json.loads(obj.user_agent_data) if obj.user_agent_data else None,
                'form_data': json.loads(obj.form_data) if obj.form_data else None,
                'warnings': warnings
            }
        )
        
        return format_html('{}', mark_safe(modal_html))
    
    metadata.short_description = 'Metadata'  # type: ignore
    
    class Media:
        css = {
            'all': (
                'admin_interface/magnific-popup/magnific-popup.css',
                'admin_interface/tabbed-changeform/tabbed-changeform.css',
                '.metadata-icon { margin-right: 5px; }',
                '.metadata-icon:hover { cursor: pointer; opacity: 0.7; }',
                '.warning-icon { margin-right: 5px; color: #ff9800; }',
                '.warning-icon:hover { cursor: pointer; opacity: 0.7; }',
            )
        }
        js = (
            'admin/js/vendor/jquery/jquery.min.js',
            'admin_interface/magnific-popup/jquery.magnific-popup.min.js',
            'admin_interface/magnific-popup/magnific-popup-init.js',
            'admin_interface/tabbed-changeform/tabbed-changeform.js',
        )


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
