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
    
    fields = ('id','server_timestamp', 'http_method', 'pretty_headers_data', 'pretty_ip_data', 'pretty_browser_data', 'pretty_form_data')
    readonly_fields = ('server_timestamp', 'display_client_time',)
    search_fields = ('http_method')
    list_filter = ('http_method')
    list_per_page = 20
    
    readonly_fields = ('server_timestamp', 'pretty_headers_data', 'pretty_ip_data', 'pretty_browser_data', 'pretty_form_data')

    @admin.display(description='Form Data')
    def pretty_form_data(self, obj):
        if not obj.form_data:
            return "-"
        try:
            pretty_json = json.dumps(obj.form_data, indent=4)
            return mark_safe(f'<pre style="white-space: pre-wrap;">{pretty_json}</pre>')
        except Exception:
            return str(obj.form_data)

    @admin.display(description='Headers Data')
    def pretty_headers_data(self, obj):
        if not obj.headers_data:
            return "-"
        try:
            pretty_json = json.dumps(obj.headers_data, indent=4)
            return mark_safe(f'<pre style="white-space: pre-wrap;">{pretty_json}</pre>')
        except Exception:
            return str(obj.headers_data)

    @admin.display(description='IP Data')
    def pretty_ip_data(self, obj):
        if not obj.ip_data:
            return "-"
        try:
            pretty_json = json.dumps(obj.ip_data, indent=4)
            return mark_safe(f'<pre style="white-space: pre-wrap;">{pretty_json}</pre>')
        except Exception:
            return str(obj.ip_data)

    @admin.display(description='Browser Data')
    def pretty_browser_data(self, obj):
        if not obj.user_agent_data:
            return "-"
        try:
            pretty_json = json.dumps(obj.user_agent_data, indent=4)
            return mark_safe(f'<pre style="white-space: pre-wrap;">{pretty_json}</pre>')
        except Exception:
            return str(obj.user_agent_data)

    @admin.display(description='Client Time')
    def display_client_time(self, obj):
        if obj.client_timestamp and obj.client_timezone:
            dt = parse_client_timestamp(obj.client_timestamp.isoformat(), obj.client_timezone)
            if dt:
                return dt.strftime('%Y-%m-%d %I:%M %p')
        return '-'


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
            'ip_tracking', 'location_tracking', 'locale_tracking', 'browser_tracking', 'time_tracking'
        )}),
    )
    subadmins=[AgentAdmin]
