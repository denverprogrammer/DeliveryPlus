from django.contrib import admin, messages
from django.utils.html import format_html
from subadmin import SubAdmin, RootSubAdmin
from delivery.models import Company, Agent, TrackingData
from datetime import datetime
from zoneinfo import ZoneInfo


def parse_client_timestamp(datetime_str, timezone_str):
    try:
        client_tz = ZoneInfo(timezone_str) if timezone_str else ZoneInfo('UTC')
        dt_object = datetime.fromisoformat(datetime_str)

        return dt_object.astimezone(client_tz)
    except ValueError as e:
        print(f"Error parsing datetime string: {e}")
        return None

class TrackingDataInline(admin.TabularInline):
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
    
    fields = ('server_timestamp', 'http_method', 'ip_address', 'display_client_time', 'client_timezone', 'latitude', 'longitude', 'user_agent')
    readonly_fields = ('server_timestamp', 'display_client_time',)
    search_fields = ('ip_address', 'user_agent', 'http_method', 'client_timezone', 'client_timezone')
    list_filter = ('http_method', 'client_timezone')
    list_per_page = 20

    @admin.display(description="Client Time")
    def display_client_time(self, obj):
        if obj.client_timestamp and obj.client_timezone:
            dt = parse_client_timestamp(obj.client_timestamp.isoformat(), obj.client_timezone)
            if dt:
                return dt.strftime("%Y-%m-%d %I:%M %p")
        return "-"

class AgentAdmin(SubAdmin):
    parent_model = Company
    model = Agent
    inlines = [TrackingDataInline] 
    list_display = ("id", "first_name", "last_name", "email", "phone_number", "status_display", "token")
    search_fields = ("first_name", "last_name", "email", "phone_number")
    list_filter = ("status",)
    actions = ["deactivate_agents"]

    def save_model(self, request, obj, form, change):
        if not change and not obj.company_id:
            obj.company = self.parent_object
        super().save_model(request, obj, form, change)
        if not change:
            messages.success(request, f"Agent '{obj.first_name} {obj.last_name}' was successfully created.")
        else:
            messages.success(request, f"Agent '{obj.first_name} {obj.last_name}' was successfully updated.")

    @admin.display(description="Status")
    def status_display(self, obj):
        color = "green" if obj.status == "active" else "red"
        return format_html('<strong style="color: {}">{}</strong>', color, obj.status.capitalize())

    @admin.action(description="Deactivate selected agents")
    def deactivate_agents(self, request, queryset):
        updated = queryset.update(status="inactive")
        self.message_user(request, f"{updated} agent(s) were successfully deactivated.", messages.SUCCESS)


@admin.register(Company)
class CompanyAdmin(RootSubAdmin):
    subadmins = [AgentAdmin]
    # inlines = [AgentInline]
    list_display = ("name", "agent_count")
    search_fields = ("name",)
    list_filter = ()

    def agent_count(self, obj):
        return obj.agents.count()
    agent_count.short_description = "#Agents"