from typing import Any
from typing import List
from typing import Tuple
from typing import Type
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


def process_list_filter(list_filter: tuple | list) -> tuple[Any, ...]:
    """
    Process list_filter to convert tuple syntax to configured filter classes.

    Converts ("field_name", BaseTextFieldFilter) to a configured filter class.

    Args:
        list_filter: The list_filter tuple/list from admin class

    Returns:
        Processed list_filter with tuples converted to filter classes

    Usage in admin.py:
        list_filter = process_list_filter([
            ("first_name", BaseTextFieldFilter),
            ("recipient__email", BaseTextFieldFilter),
            "status",  # Built-in filters pass through unchanged
        ])
    """
    processed: list[Any] = []
    for item in list_filter:
        if isinstance(item, tuple) and len(item) == 2:
            field_path, filter_class = item
            if filter_class is BaseTextFieldFilter:
                # Convert tuple to configured filter class
                processed.append(text_field_filter(field_path))
            else:
                # Pass through other tuple filters unchanged
                processed.append(item)
        else:
            # Pass through non-tuple filters unchanged
            processed.append(item)
    return tuple(processed)


def text_field_filter(field_path: str, title: str | None = None) -> Type[BaseTextFieldFilter]:
    """
    Factory function to create a text field filter class for a given field path.

    Args:
        field_path: The field path to filter on (e.g., "first_name", "recipient__email")
        title: Optional display title (defaults to field_path with underscores replaced)

    Returns:
        A filter class configured for the specified field

    Usage in admin.py:
        list_filter = [
            text_field_filter("first_name"),
            text_field_filter("recipient__email", "Recipient Email"),
        ]
    """
    # Extract parameter name from field path (last part after __)
    parameter_name = field_path.split("__")[-1]

    # Generate title from parameter name if not provided
    if title is None:
        title = parameter_name.replace("_", " ").title()

    # Create a new class dynamically
    filter_class = type(
        f"{parameter_name.title().replace(' ', '').replace('_', '')}Filter",
        (BaseTextFieldFilter,),
        {
            "title": title,
            "parameter_name": parameter_name,
            "field_name": field_path,
        },
    )
    return filter_class
