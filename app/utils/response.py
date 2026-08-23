from datetime import datetime, timezone
from typing import Any
from fastapi import Request


def make_success_response(status_code: int, message: str, data: Any, request: Request):
    return {
        "statusCode": status_code,
        "message": message,
        "error": None,
        "data": data,
        "url": request.url.path,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
