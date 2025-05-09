from django.contrib import admin
from typing import Any, List, Tuple, Type, Dict
# from django.utils.safestring import mark_safe
from django.http import HttpRequest
from subadmin import SubAdmin  # type: ignore
from tracking.models import Agent
from django.db.models import QuerySet, Model


class BaseTextFieldFilter(admin.SimpleListFilter):
    """Base class for text field filters."""
    template = 'admin/text_field_filter.html'
    field_name = ''

    def __init__(self, request: HttpRequest, params: Dict[str, Any], model: Type[Model], model_admin: Any) -> None:
        super().__init__(request, params, model, model_admin) # type: ignore

    def lookups(self, request: HttpRequest, model_admin: Any) -> List[Tuple[str, str]]:
        return [(self.field_name, self.title)]

    def queryset(self, request: HttpRequest, queryset: QuerySet[Agent]) -> QuerySet[Agent]:
        if self.value():
            search_term = request.GET.get(f'{self.parameter_name}_term', '')
            if search_term:
                return queryset.filter(**{f"{self.field_name}__icontains": search_term})
        return queryset


class FirstNameFilter(BaseTextFieldFilter):
    title = 'First Name'
    parameter_name = 'first_name'
    field_name = 'first_name'


class LastNameFilter(BaseTextFieldFilter):
    title = 'Last Name'
    parameter_name = 'last_name'
    field_name = 'last_name'


class EmailFilter(BaseTextFieldFilter):
    title = 'Email'
    parameter_name = 'email'
    field_name = 'email'


class PhoneNumberFilter(BaseTextFieldFilter):
    title = 'Phone Number'
    parameter_name = 'phone_number'
    field_name = 'phone_number'


class TokenFilter(BaseTextFieldFilter):
    title = 'Token'
    parameter_name = 'token'
    field_name = 'token'
