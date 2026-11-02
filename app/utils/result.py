# app/utils/result.py
from __future__ import annotations

import time
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

from app.utils.error_code import ErrorCode

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None
    success: bool = True
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000))

    @classmethod
    def ok(cls, data: T = None, message: str = "success", code: int = ErrorCode.SUCCESS) -> "Result[T]":
        return cls(code=code, message=message, data=data, success=True)

    @classmethod
    def fail(cls, message: str = "error", code: int = ErrorCode.SERVER_ERROR, data: T = None) -> "Result[T]":
        return cls(code=code, message=message, data=data, success=False)
