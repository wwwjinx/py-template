# app/utils/error_code.py
from enum import IntEnum

class ErrorCode(IntEnum):
    SUCCESS = 200
    PARAM_ERROR = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    SERVER_ERROR = 500
