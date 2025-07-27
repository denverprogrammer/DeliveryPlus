from typing import Any
from typing import List
from typing import Tuple
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from tracking.models import Agent


class BaseTextFieldFilter(admin.SimpleListFilter):
    """Base class for text field filters."""

    template = "admin/text_field_filter.html"
    field_name = ""

    def lookups(self, request: HttpRequest, model_admin: Any) -> List[Tuple[str, str]]:
        return [(self.field_name, str(self.title))]

    def queryset(self, request: HttpRequest, queryset: QuerySet[Agent]) -> QuerySet[Agent]:
        if self.value():
            search_term = request.GET.get(f"{self.parameter_name}_term", "")
            if search_term:
                return queryset.filter(**{f"{self.field_name}__icontains": search_term})
        return queryset


class TagFilter(BaseTextFieldFilter):
    """Filter agents by tag name."""

    title = "Tags"
    parameter_name = "tags"
    field_name = "tags__name"


class FirstNameFilter(BaseTextFieldFilter):
    title = "First Name"
    parameter_name = "first_name"
    field_name = "first_name"


class LastNameFilter(BaseTextFieldFilter):
    title = "Last Name"
    parameter_name = "last_name"
    field_name = "last_name"


class EmailFilter(BaseTextFieldFilter):
    title = "Email"
    parameter_name = "email"
    field_name = "email"


class PhoneNumberFilter(BaseTextFieldFilter):
    title = "Phone Number"
    parameter_name = "phone_number"
    field_name = "phone_number"


class TokenFilter(BaseTextFieldFilter):
    title = "Token"
    parameter_name = "token"
    field_name = "token"
