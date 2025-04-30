from typing import Any
from django import template

register = template.Library()

@register.filter
def get_field(form: Any, field_name: str):
    """Get a form field by name."""
    return form[field_name] 