from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

from .exception import AppException


def http_exeption_handler(req: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "statusCode": exc.status_code,
            "message": exc.detail,
            "error": exc.error,
            "data": None,
            "url": req.url.path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
