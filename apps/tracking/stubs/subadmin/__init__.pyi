from typing import Any
from typing import Type
from typing import TypeVar
from django.contrib import admin

T = TypeVar("T", bound=Any)

class SubAdmin(admin.ModelAdmin[T]):
    """Base class for subadmin."""

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class RootSubAdmin(admin.ModelAdmin[T]):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
