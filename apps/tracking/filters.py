from typing import Any
from typing import List
from typing import Tuple
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest


class BaseTextFieldFilter(admin.SimpleListFilter):
    """Generic base class for text field filters that works with any model."""

    template = "admin/text_field_filter.html"
    field_name = ""

    def lookups(self, request: HttpRequest, model_admin: Any) -> List[Tuple[str, str]]:
        return [(self.field_name, str(self.title))]

    def queryset(self, request: HttpRequest, queryset: QuerySet[Any]) -> QuerySet[Any]:
        search_term = self.value()
        if search_term:
            return queryset.filter(**{f"{self.field_name}__icontains": search_term})
        return queryset


class TrackingFirstNameFilter(BaseTextFieldFilter):
    title = "First Name"
    parameter_name = "first_name"
    field_name = "recipient__first_name"


class TrackingLastNameFilter(BaseTextFieldFilter):
    title = "Last Name"
    parameter_name = "last_name"
    field_name = "recipient__last_name"


class TrackingPhoneNumberFilter(BaseTextFieldFilter):
    title = "Phone Number"
    parameter_name = "phone_number"
    field_name = "recipient__phone_number"


class TrackingTokenFilter(BaseTextFieldFilter):
    title = "Token"
    parameter_name = "token"
    field_name = "token"


class TrackingEmailFilter(BaseTextFieldFilter):
    title = "Email"
    parameter_name = "email"
    field_name = "recipient__email"


class TrackingCampaignNameFilter(BaseTextFieldFilter):
    title = "Campaign Name"
    parameter_name = "campaign_name"
    field_name = "campaign__name"


class RecipientFirstNameFilter(BaseTextFieldFilter):
    title = "First Name"
    parameter_name = "first_name"
    field_name = "first_name"


class RecipientLastNameFilter(BaseTextFieldFilter):
    title = "Last Name"
    parameter_name = "last_name"
    field_name = "last_name"


class RecipientPhoneNumberFilter(BaseTextFieldFilter):
    title = "Phone"
    parameter_name = "phone_number"
    field_name = "phone_number"


class RecipientTagsFilter(BaseTextFieldFilter):
    title = "Tags"
    parameter_name = "tags"
    field_name = "tags__name"


class RecipientEmailFilter(BaseTextFieldFilter):
    title = "Email"
    parameter_name = "email"
    field_name = "email"
