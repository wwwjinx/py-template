from __future__ import annotations

from enum import IntEnum


class ResponseCode(IntEnum):
    SUCCESS = 200
    PARAM_ERROR = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    SERVER_ERROR = 500


class ResponseMsg:
    SUCCESS = "success"
    ERROR = "error"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not found"
    PARAM_ERROR = "param error"


# Backward-compatible alias used by existing routes
ErrorCode = ResponseCode

__all__ = ["ResponseCode", "ResponseMsg", "ErrorCode"]
