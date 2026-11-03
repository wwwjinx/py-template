import time
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

from app.enums import ResponseCode

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    """Unified API envelope (koa-style: HTTP often stays 200, `code` carries semantics)."""

    code: int = 200
    message: str = "success"
    data: Optional[T] = None
    success: bool = True
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000))

    @classmethod
    def ok(
        cls,
        data: T = None,
        message: str = "success",
        code: int = ResponseCode.SUCCESS,
    ) -> "Result[T]":
        return cls(code=int(code), message=message, data=data, success=True)

    @classmethod
    def fail(
        cls,
        message: str = "error",
        code: int = ResponseCode.SERVER_ERROR,
        data: T = None,
    ) -> "Result[T]":
        return cls(code=int(code), message=message, data=data, success=False)
