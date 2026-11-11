from pydantic import BaseModel

from app.enums import ResponseCode


class Result[T](BaseModel):
    """Unified API envelope in RuoYi format: `{code, data, msg}`. HTTP often stays 200."""

    code: int = 200
    data: T | None = None
    msg: str = "success"

    @classmethod
    def ok(
        cls,
        data: T = None,
        msg: str = "success",
        code: int = ResponseCode.SUCCESS,
    ) -> Result[T]:
        return cls(code=int(code), msg=msg, data=data)

    @classmethod
    def fail(
        cls,
        msg: str = "error",
        code: int = ResponseCode.SERVER_ERROR,
        data: T = None,
    ) -> Result[T]:
        return cls(code=int(code), msg=msg, data=data)
