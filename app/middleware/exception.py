from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import config
from app.core.exceptions import AppException
from app.enums import ResponseCode, ResponseMsg
from app.log import get_logger
from app.utils.result import Result

logger = get_logger("app.error")


def _result_response(result: Result, http_status: int = 200) -> JSONResponse:
    # Keep HTTP 200 and put semantics in body.code (RuoYi-style envelope).
    # Callers can still pass another http_status if needed later.
    return JSONResponse(status_code=http_status, content=result.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
        logger.error("AppException code=%s message=%s", exc.code, exc.message)
        if config.IS_DEV:
            print("====================")
            print(exc)
            print("====================")
        return _result_response(Result.fail(msg=exc.message, code=exc.code, data=exc.data))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("validation error: %s", exc.errors())
        return _result_response(
            Result.fail(
                msg=ResponseMsg.PARAM_ERROR,
                code=ResponseCode.PARAM_ERROR,
                data=exc.errors(),
            )
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = exc.status_code
        message = exc.detail if isinstance(exc.detail, str) else ResponseMsg.ERROR
        if code == 404:
            code = ResponseCode.NOT_FOUND
            message = message if isinstance(exc.detail, str) else ResponseMsg.NOT_FOUND
        logger.warning("HTTPException status=%s detail=%s", exc.status_code, exc.detail)
        return _result_response(Result.fail(msg=str(message), code=int(code)))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        if config.IS_DEV:
            logger.exception("unhandled error")
        else:
            logger.error("unhandled error: %s", exc)
        return _result_response(
            Result.fail(msg=ResponseMsg.ERROR, code=ResponseCode.SERVER_ERROR)
        )
