import base64
import json
import logging
from typing import Callable
from django.http import HttpRequest, HttpResponse
from config.common import HeaderData

logger = logging.getLogger(__name__)

class TrackingPayloadMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        header_value = request.headers.get('X-Tracking-Payload')

        if header_value:
            try:
                # Step 1: Decode base64 safely
                decoded_bytes = base64.b64decode(header_value)
                decoded_str = decoded_bytes.decode('utf-8')

                # Step 2: Parse JSON
                payload: HeaderData = HeaderData(**json.loads(decoded_str))

                # Step 3: Attach to request
                setattr(request, 'headers_data', payload)
            # except (ValueError, json.JSONDecodeError, base64.binascii.Error) as e:
            except (ValueError, json.JSONDecodeError) as e:
                logger.warning(f"Invalid tracking payload: {e}")
                setattr(request, 'headers_data', None)
        else:
            # No header found
            setattr(request, 'headers_data', None)

        response = self.get_response(request)
        return response
