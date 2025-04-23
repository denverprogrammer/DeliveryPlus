import json
from django.contrib import admin, messages
from django.utils.html import format_html
from subadmin import SubAdmin
from tracking.forms import CampaignAdminForm
from tracking.models import TrackingData, Agent, Campaign
from datetime import datetime
from zoneinfo import ZoneInfo
from django.utils.safestring import mark_safe


def parse_client_timestamp(datetime_str, timezone_str):
    try:
        client_tz = ZoneInfo(timezone_str) if timezone_str else ZoneInfo('UTC')
        dt_object = datetime.fromisoformat(datetime_str)

        return dt_object.astimezone(client_tz)
    except ValueError as e:
        print(f'Error parsing datetime string: {e}')
        return None


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
        'user_agent',
        'user_agent_source',
        'locale',
        'locale_source',
        'client_time',
        'time_source',
        'client_timezone',
        'latitude',
        'longitude',
        'location_source',
        'warnings',
        'data_icons'
    )
    readonly_fields = (
        'server_timestamp',
        'ip_address',
        'ip_source',
        'user_agent',
        'user_agent_source',
        'locale',
        'locale_source',
        'client_time',
        'time_source',
        'client_timezone',
        'latitude',
        'longitude',
        'location_source',
        'warnings',
        'data_icons'
    )
    search_fields = ('http_method',)
    list_filter = ('http_method',)
    list_per_page = 20

    def warnings(self, obj):
        warnings = []
        
        # Check for IP address mismatch
        if obj.ip_data:
            server_ip = obj.ip_data.get('server_ip', {}).get('address')
            header_ip = obj.ip_data.get('header_ip', {}).get('address')
            
            if server_ip and header_ip and server_ip != header_ip:
                warning_html = format_html(
                    '<span class="warning-icon" title="IP Address Mismatch: Server IP ({}) differs from Client IP ({})">⚠️</span>',
                    server_ip,
                    header_ip
                )
                warnings.append(warning_html)
        
        return mark_safe(' '.join(warnings)) if warnings else '-'
    
    warnings.short_description = 'Warnings'

    def data_icons(self, obj):
        icons = []
        
        # Headers Data Icon
        if obj.headers_data:
            headers_html = format_html(
                '<span class="data-icon" title="{}">📋</span>',
                json.dumps(obj.headers_data, indent=2)
            )
            icons.append(headers_html)
        
        # IP Data Icon
        if obj.ip_data:
            ip_html = format_html(
                '<span class="data-icon" title="{}">🌐</span>',
                json.dumps(obj.ip_data, indent=2)
            )
            icons.append(ip_html)
        
        # User Agent Data Icon
        if obj.user_agent_data:
            ua_html = format_html(
                '<span class="data-icon" title="{}">🖥️</span>',
                json.dumps(obj.user_agent_data, indent=2)
            )
            icons.append(ua_html)
        
        # Form Data Icon
        if obj.form_data:
            form_html = format_html(
                '<span class="data-icon" title="{}">📝</span>',
                json.dumps(json.loads(obj.form_data), indent=2)
            )
            icons.append(form_html)
        
        return mark_safe(' '.join(icons))
    
    data_icons.short_description = 'Data'
    
    class Media:
        css = {
            'all': (
                '.data-icon { cursor: help; margin-right: 5px; }',
                '.data-icon:hover { opacity: 0.7; }',
                '.warning-icon { cursor: help; margin-right: 5px; color: #ff9800; }',
                '.warning-icon:hover { opacity: 0.7; }',
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
