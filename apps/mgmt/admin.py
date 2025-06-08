from django.contrib import admin
from mgmt.models import Company
from mgmt.models import User
from subadmin import RootSubAdmin
from tracking.admin import CampaignAdmin


@admin.register(Company)
class CompanyAdmin(RootSubAdmin[Company]):
    list_display = ("name", "city", "state", "country", "phone_number")
    search_fields = ("name", "city", "state", "country")
    subadmins = [CampaignAdmin]


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin[User]):
    list_display = ("username", "email", "company", "is_active", "is_staff")
    search_fields = ("username", "email")
    list_filter = ("company", "is_active", "is_staff")
