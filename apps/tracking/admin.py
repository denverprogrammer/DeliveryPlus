import json
from django.contrib import admin, messages
from django.utils.html import format_html
from subadmin import SubAdmin
from tracking.forms import CampaignAdminForm
from tracking.models import TrackingData, Agent, Campaign
from datetime import datetime
from zoneinfo import ZoneInfo
from django.utils.safestring import mark_safe
from typing import Optional


class TrackingDataInline(admin.TabularInline): # type: ignore
    model = TrackingData
    extra = 0
    show_change_link = False
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.order_by('-server_timestamp')
    
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
    readonly_fields = (
        'server_timestamp',
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
    search_fields = ('http_method',)
    list_filter = ('http_method',)
    list_per_page = 20

    def check_ip_mismatch(self, obj: TrackingData) -> Optional[str]:
        if not obj.ip_data:
            return None

        ip_data = json.loads(obj.ip_data) if isinstance(obj.ip_data, str) else obj.ip_data
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
        if not obj.ip_data:
            return None
        ip_data = json.loads(obj.ip_data) if isinstance(obj.ip_data, str) else obj.ip_data

        if ip_data.get('info', {}).get('security', {}).get('is_vpn'):
            return format_html(
                '<span class="warning-icon" title="VPN/Proxy Detected">🔒</span>'
            )

        return None

    def check_crawler(self, obj: TrackingData) -> Optional[str]:
        if not obj.user_agent_data:
            return None

        ua_data = json.loads(obj.user_agent_data) if isinstance(obj.user_agent_data, str) else obj.user_agent_data

        if ua_data.get('info', {}).get('crawler', {}).get('is_crawler'):
            return format_html(
                '<span class="warning-icon" title="Crawler/Bot Detected">🤖</span>'
            )

        return None

    def check_user_agent_mismatch(self, obj: TrackingData) -> Optional[str]:
        if not obj.user_agent_data:
            return None

        ua_data = json.loads(obj.user_agent_data) if isinstance(obj.user_agent_data, str) else obj.user_agent_data

        if ua_data.get('server_user_agent') != ua_data.get('header_user_agent'):
            return format_html(
                '<span class="warning-icon" title="User Agent Mismatch: Server and Client user agents differ">🔄</span>'
            )

        return None

    def check_timezone_mismatch(self, obj: TrackingData) -> Optional[str]:
        if not obj.headers_data and obj.ip_data:
            return None

        header_timezone = obj.headers_data.get('datetime', {}).get('timezone')
        ip_timezone = obj.ip_data.get('info', {}).get('timezone').get('name')

        if header_timezone != ip_timezone:
            return format_html(
                '<span class="warning-icon" title="Non-UTC Timezone: {}">⏰</span>',
                obj.client_timezone
            )

        return None

    def check_security(self, obj: TrackingData) -> Optional[str]:
        if not obj.ip_data:
            return None
        
        ip_data = json.loads(obj.ip_data) if isinstance(obj.ip_data, str) else obj.ip_data
        security = ip_data.get('info', {}).get('security', {})
        
        warnings = []
        if security.get('vpn'):
            warnings.append('VPN')
        if security.get('proxy'):
            warnings.append('Proxy')
        if security.get('tor'):
            warnings.append('Tor')
        if security.get('relay'):
            warnings.append('Relay')
        if security.get('hosting'):
            warnings.append('Hosting')
        
        if warnings:
            return format_html(
                '<span class="warning-icon" title="Security Issues: {}">🔒</span>',
                ', '.join(warnings)
            )
        return None

    def warnings(self, obj: TrackingData):
        warnings = []
        
        # Check for IP address mismatch
        if warning := self.check_ip_mismatch(obj):
            warnings.append(warning)

        # Check for VPN/Proxy
        if warning := self.check_vpn(obj):
            warnings.append(warning)

        # Check for security issues
        if warning := self.check_security(obj):
            warnings.append(warning)

        # Check for suspicious browser
        if warning := self.check_crawler(obj):
            warnings.append(warning)

        # Check for user agent mismatch
        if warning := self.check_user_agent_mismatch(obj):
            warnings.append(warning)

        # Check for timezone mismatch
        if warning := self.check_timezone_mismatch(obj):
            warnings.append(warning)
        
        return mark_safe(' '.join(warnings)) if warnings else '-'
    
    warnings.short_description = 'Warnings'

    def metadata(self, obj):
        icons = []
        
        # Headers Data Icon
        if obj.headers_data:
            headers_html = format_html(
                '<span class="metadata-icon" title="{}">📋</span>',
                json.dumps(json.loads(obj.headers_data), indent=4, ensure_ascii=False)
            )
            icons.append(headers_html)
        
        # IP Data Icon
        if obj.ip_data:
            ip_html = format_html(
                '<span class="metadata-icon" title="{}">🌐</span>',
                json.dumps(json.loads(obj.ip_data), indent=4, ensure_ascii=False)
            )
            icons.append(ip_html)
        
        # User Agent Data Icon
        if obj.user_agent_data:
            ua_html = format_html(
                '<span class="metadata-icon" title="{}">🖥️</span>',
                json.dumps(json.loads(obj.user_agent_data), indent=4, ensure_ascii=False)
            )
            icons.append(ua_html)
        
        # Form Data Icon
        if obj.form_data:
            form_html = format_html(
                '<span class="metadata-icon" title="{}">📝</span>',
                json.dumps(json.loads(obj.form_data), indent=4, ensure_ascii=False)
            )
            icons.append(form_html)
        
        return mark_safe(' '.join(icons))
    
    metadata.short_description = 'Metadata'
    
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
    model=Agent
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'status')}),
        ('Contact', {'fields': ('token', 'email', 'phone_number')}),
    )
    
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'status')
    list_filter = ('status',)
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    ordering = ('first_name',)
    inlines=[TrackingDataInline]


class CampaignAdmin(SubAdmin):
    model=Campaign
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
    subadmins=[AgentAdmin]
