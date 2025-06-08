from typing import Any
from typing import Optional
from typing import Type
from typing import TypeVar
from django import forms
from django.db import models

T = TypeVar("T", bound=models.Model)

class TagField(forms.Field):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def clean(self, value: Any) -> Any: ...

class TagWidget(forms.Widget):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
