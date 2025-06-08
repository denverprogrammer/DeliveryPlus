from django import template
from django.forms import BoundField
from django.forms import Form


register = template.Library()


@register.filter
def get_field(form: Form, field_name: str) -> BoundField:
    """Get a form field by name."""
    return form[field_name]
