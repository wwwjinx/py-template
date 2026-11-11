from typing import Any

from app.enums import ResponseCode, ResponseMsg


class AppException(Exception):
    """业务/应用异常，由全局处理器转成 Result.fail（HTTP 200，body 为若依格式）。"""

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
    """业务失败的别名，用法与 AppException 相同。"""
