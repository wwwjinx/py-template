from typing import Any

from app.enums import ResponseCode, ResponseMsg


class AppException(Exception):
    """Business / application error → Result.fail (HTTP 200, body.code)."""

    def __init__(
        self,
        message: str = ResponseMsg.ERROR,
        code: int = ResponseCode.SERVER_ERROR,
        data: Any | None = None,
    ) -> None:
        self.message = message
        self.code = int(code)
        self.data = data
        super().__init__(message)


class BizException(AppException):
    """Alias for domain/business failures."""
