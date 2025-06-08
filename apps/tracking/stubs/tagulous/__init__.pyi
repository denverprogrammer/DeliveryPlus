from typing import Any
from typing import Type
from typing import TypeVar
from . import admin
from . import forms
from . import models

T = TypeVar("T")

class TagModel:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class TagField:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

__all__ = ["admin", "forms", "models"]
