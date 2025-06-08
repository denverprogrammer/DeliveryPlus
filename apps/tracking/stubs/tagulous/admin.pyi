from typing import Any
from typing import Type
from typing import TypeVar

T = TypeVar("T")

class TaggedModelAdmin:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

def enhance(model: Type[T], admin_class: Type[Any]) -> None: ...
