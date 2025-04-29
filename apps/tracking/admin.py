from django.contrib import admin
from typing import Optional, Any, List
from django.utils.html import format_html
# from django.utils.safestring import mark_safe
from django.http import HttpRequest
from django.urls import reverse
from subadmin import SubAdmin  # type: ignore
from tracking.forms import CampaignAdminForm
from tracking.models import TrackingData, Agent, Campaign
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget # type: ignore
import json


# @admin.register(TrackingData)
# class TrackingDataAdmin(admin.ModelAdmin):  # type: ignore
#     model = TrackingData
#     fieldsets = (
#         ('Basic Information', {
#             'fields': (
#                 'server_timestamp',
#                 'http_method',
#                 'ip_address',
#                 'ip_source',
#             )
#         }),
#         ('Client Information', {
#             'fields': (
#                 'os',
#                 'browser',
#                 'platform',
#                 'locale',
#                 'client_time',
#                 'client_timezone',
#             )
#         }),
#         ('Location Information', {
#             'fields': (
#                 'latitude',
#                 'longitude',
#                 'location_source',
#                 'location_map',
#             ),
#             'classes': ('collapse',)
#         }),
#         ('Data Fields', {
#             'fields': (
#                 'pretty_ip_data',
#                 'pretty_user_agent_data',
#                 'pretty_header_data',
#                 'pretty_form_data'
#             ),
#             'classes': ('collapse',)
#         }),
#         ('Security Checks', {
#             'fields': (
#                 'ip_mismatch',
#                 'country_mismatch',
#                 'user_agent_mismatch',
#                 'timezone_mismatch',
#                 'locale_mismatch',
#                 'crawler_detection',
#                 'suspicious_activity',
#                 'data_consistency'
#             ),
#             'classes': ('collapse',)
#         })
#     )
#     readonly_fields = (
#         'server_timestamp', 'http_method', 'ip_address', 'ip_source',
#         'os', 'browser', 'platform', 'locale', 'client_time', 'client_timezone',
#         'latitude', 'longitude', 'location_source', 'location_map',
#         'pretty_ip_data', 'pretty_user_agent_data', 'pretty_header_data', 'pretty_form_data',
#         'ip_mismatch', 'country_mismatch', 'user_agent_mismatch',
#         'timezone_mismatch', 'locale_mismatch',
#         'crawler_detection', 'suspicious_activity', 'data_consistency'
#     )
#     formfield_overrides = {
#         JSONField: {
#             'widget': JSONEditorWidget(
#                 attrs={
#                     'readonly': True,
#                     'style': 'height: 300px;'
#                 }
#             )
#         }
#     }

#     class Media:
#         css = {
#             'all': (
#                 'https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/9.10.0/jsoneditor.min.css',
#             )
#         }
#         js = (
#             'https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/9.10.0/jsoneditor.min.js',
#         )

#     def has_add_permission(self, request: HttpRequest, obj: Optional[TrackingData] = None) -> bool:
#         return False

#     def has_change_permission(self, request: HttpRequest, obj: Optional[TrackingData] = None) -> bool:
#         return False
    
#     def has_list_view(self, request: HttpRequest, obj: Optional[TrackingData] = None) -> bool:
#         return False

#     def pretty_ip_data(self, obj: TrackingData) -> str:
#         """Display pretty-printed IP data."""
#         if not obj.ip_data:
#             return 'No IP data available'
#         return format_html(
#             '<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; font-family: monospace; white-space: pre-wrap;">{}</pre>',
#             json.dumps(obj.ip_data.model_dump(), indent=2, sort_keys=True)
#         )
#     pretty_ip_data.short_description = 'IP Data'  # type: ignore

#     def pretty_user_agent_data(self, obj: TrackingData) -> str:
#         """Display pretty-printed user agent data."""
#         if not obj.user_agent_data:
#             return 'No user agent data available'
#         return format_html(
#             '<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; font-family: monospace; white-space: pre-wrap;">{}</pre>',
#             json.dumps(obj.user_agent_data.model_dump(), indent=2, sort_keys=True)
#         )
#     pretty_user_agent_data.short_description = 'User Agent Data'  # type: ignore

#     def pretty_header_data(self, obj: TrackingData) -> str:
#         """Display pretty-printed header data."""
#         if not obj.header_data:
#             return 'No header data available'
#         return format_html(
#             '<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; font-family: monospace; white-space: pre-wrap;">{}</pre>',
#             json.dumps(obj.header_data.model_dump(), indent=2, sort_keys=True)
#         )
#     pretty_header_data.short_description = 'Header Data'  # type: ignore

#     def pretty_form_data(self, obj: TrackingData) -> str:
#         """Display pretty-printed form data."""
#         if not obj.form_data:
#             return 'No form data available'
#         return format_html(
#             '<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; font-family: monospace; white-space: pre-wrap;">{}</pre>',
#             json.dumps(obj.form_data, indent=2, sort_keys=True)
#         )
#     pretty_form_data.short_description = 'Form Data'  # type: ignore

#     def ip_mismatch(self, obj: TrackingData) -> str:
#         """Check for IP address mismatches between server and client."""
#         ip_data = obj.ip_data
        
#         if not ip_data:
#             return 'No IP data available'

#         server_ip = ip_data.getServerIpAddress()
#         header_ip = ip_data.getHeaderIpAddress()
        
#         if server_ip and header_ip and server_ip != header_ip:
#             return format_html(
#                 '<span style="color: #ff9800;">⚠️ IP Address Mismatch: Server IP ({}) differs from Header IP ({})</span>',
#                 server_ip,
#                 header_ip
#             )
#         return '✅ IP addresses match'

#     def country_mismatch(self, obj: TrackingData) -> str:
#         """Check for country mismatches between server and client."""
#         ip_data = obj.ip_data
#         header_data = obj.header_data 

#         if not ip_data or not header_data:
#             return 'No data available for comparison'

#         server_country = ip_data.getSelectedCountry()
#         header_country = header_data.getHeaderCountry()
        
#         if server_country and header_country and server_country != header_country:
#             return format_html(
#                 '<span style="color: #ff9800;">⚠️ Country Mismatch: Server country ({}) differs from Header country ({})</span>',
#                 server_country,
#                 header_country
#             )
#         return '✅ Countries match'

#     def crawler_detection(self, obj: TrackingData) -> str:
#         """Check for crawler/bot detection."""
#         user_agent_data = obj.user_agent_data

#         if not user_agent_data:
#             return 'No user agent data available'

#         if user_agent_data.is_crawler():
#             return format_html(
#                 '<span style="color: #ff9800;">⚠️ Crawler/Bot Detected</span>'
#             )
#         return '✅ No crawler detected'

#     def user_agent_mismatch(self, obj: TrackingData) -> str:
#         """Check for user agent mismatches."""
#         user_agent_data = obj.user_agent_data

#         if not user_agent_data:
#             return 'No user agent data available'

#         if user_agent_data.header != user_agent_data.server:
#             return format_html(
#                 '<span style="color: #ff9800;">⚠️ User Agent Mismatch: Server and Client user agents differ</span>'
#             )
#         return '✅ User agents match'

#     def timezone_mismatch(self, obj: TrackingData) -> str:
#         """Check for timezone mismatches."""
#         ip_data = obj.ip_data
#         header_data = obj.header_data 

#         if not ip_data or not header_data:
#             return 'No data available for comparison'

#         header_timezone = header_data.getTimezone()
#         ip_timezone = ip_data.getTimezone()

#         if header_timezone != ip_timezone:
#             return format_html(
#                 '<span style="color: #ff9800;">⚠️ Timezone Mismatch: Header timezone ({}) differs from IP timezone ({})</span>',
#                 header_timezone,
#                 ip_timezone
#             )
#         return '✅ Timezones match'

#     def locale_mismatch(self, obj: TrackingData) -> str:
#         """Check for locale mismatches between server and client."""
#         ip_data = obj.ip_data
#         header_data = obj.header_data 

#         if not ip_data or not header_data:
#             return 'No data available for comparison'
        
#         server_locale = ip_data.getLocales()
#         header_locale = header_data.getLocale()
        
#         if server_locale and header_locale and server_locale[0] != header_locale:
#             return format_html(
#                 '<span style="color: #ff9800;">⚠️ Locale Mismatch: Server locale ({}) differs from Browser locale ({})</span>',
#                 server_locale[0],
#                 header_locale
#             )
#         return '✅ Locales match'

#     def suspicious_activity(self, obj: TrackingData) -> str:
#         """Check for suspicious activity patterns."""
#         warnings: List[str] = []
        
#         # Check for unusual IP patterns
#         if obj.ip_data and obj.ip_data.isVpn():
#             warnings.append('⚠️ VPN usage detected')

#         if obj.ip_data and obj.ip_data.isProxy():
#             warnings.append('⚠️ Proxy usage detected')

#         if obj.ip_data and obj.ip_data.isTor():
#             warnings.append('⚠️ Tor usage detected')

#         if obj.ip_data and obj.ip_data.isRelay():
#             warnings.append('⚠️ Relay usage detected')

#         # Check for unusual time patterns
#         if obj.client_time and obj.server_timestamp:
#             time_diff = abs((obj.client_time - obj.server_timestamp).total_seconds())
#             if time_diff > 300:  # 5 minutes
#                 warnings.append('⚠️ Significant time difference between client and server')
        
#         if warnings:
#             return format_html('<br>'.join(warnings))
#         return '✅ No suspicious activity detected'

#     def data_consistency(self, obj: TrackingData) -> str:
#         """Check for data consistency across different sources."""
#         warnings: List[str] = []
                
#         # Check location consistency
#         if obj.latitude and obj.longitude and obj.ip_data:
#             ip_lat = obj.ip_data.getLatitude()
#             ip_lon = obj.ip_data.getLongitude()
#             if ip_lat and ip_lon:
#                 if abs(ip_lat - obj.latitude) > 0.1 or abs(ip_lon - obj.longitude) > 0.1:
#                     warnings.append('⚠️ Location information mismatch')
        
#         if warnings:
#             return format_html('<br>'.join(warnings))
#         return '✅ Data consistency verified'

#     def location_map(self, obj: TrackingData) -> str:
#         """Display a map of the location with a marker."""
#         if obj.latitude and obj.longitude:
#             return format_html(
#                 '<iframe width="100%" height="300" frameborder="0" style="border: 1px solid #ccc" '
#                 'src="https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q={},{}&zoom=12" '
#                 'allowfullscreen></iframe>',
#                 obj.latitude, obj.longitude
#             )
#         return 'No location data available'
#     location_map.short_description = 'Location Map'  # type: ignore


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
        """Display a link to view the details in a modal."""
        url = reverse('tracking_data_modal', args=[obj.pk])
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
