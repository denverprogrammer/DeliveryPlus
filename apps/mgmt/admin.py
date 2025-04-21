from django.contrib import admin
from subadmin import RootSubAdmin
from tracking.admin import CampaignAdmin
from mgmt.models import Company, User


@admin.register(Company)
class CompanyAdmin(RootSubAdmin):
    list_display = ('name', 'city', 'state', 'country', 'phone_number')
    search_fields = ('name', 'city', 'state', 'country')
    subadmins=[CampaignAdmin]


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin): # type: ignore
    list_display = ('username', 'email', 'company', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('company', 'is_active', 'is_staff')
