from fastapi import HTTPException
from typing import Any


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: Any, error: str):
        super().__init__(status_code=status_code, detail=detail)
        self.error = error
