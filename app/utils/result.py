from pydantic import BaseModel

from app.enums import ResponseCode


class Result[T](BaseModel):
    """统一响应体，对齐若依格式：`{code, data, msg}`。

    HTTP 状态通常保持 200，成功或失败看 `code`：200 成功，其它为业务错误。
    """

    # 业务状态码，200 表示成功
    code: int = 200
    # 业务数据，失败时可为 None
    data: T | None = None
    # 提示信息
    msg: str = "success"

    @classmethod
    def ok(
        cls,
        data: T = None,
        msg: str = "success",
        code: int = ResponseCode.SUCCESS,
    ) -> Result[T]:
        """成功响应，默认 `code=200`、`msg=success`。"""
        return cls(code=int(code), msg=msg, data=data)

    @classmethod
    def fail(
        cls,
        msg: str = "error",
        code: int = ResponseCode.SERVER_ERROR,
        data: T = None,
    ) -> Result[T]:
        """失败响应，默认 `code=500`、`msg=error`。"""
        return cls(code=int(code), msg=msg, data=data)
