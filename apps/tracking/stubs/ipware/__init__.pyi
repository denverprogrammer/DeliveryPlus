from typing import Any
from typing import Optional
from typing import Tuple

def get_client_ip(request: Any, proxy_order: Optional[str] = None) -> Tuple[str, bool]:
    """Get client IP address from request."""
    ...

def get_real_ip(request: Any) -> Optional[str]:
    """Get real IP address from request."""
    ...

__all__ = ["get_client_ip", "get_real_ip"]
