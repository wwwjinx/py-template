"""无状态 JWT（HS256），不依赖 Redis 会话。"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt.exceptions import PyJWTError

from app import config
from app.core.exceptions import BizException
from app.enums import ResponseCode, ResponseMsg


def create_access_token(payload: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    secret = config.JWT_SECRET
    if not secret:
        raise BizException(message="JWT_SECRET is not set", code=ResponseCode.SERVER_ERROR)
    to_encode = payload.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=config.JWT_EXPIRE_MINUTES))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, secret, algorithm=config.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    secret = config.JWT_SECRET
    if not secret:
        raise BizException(message=ResponseMsg.UNAUTHORIZED, code=ResponseCode.UNAUTHORIZED)
    try:
        return jwt.decode(token, secret, algorithms=[config.JWT_ALGORITHM])
    except PyJWTError as exc:
        raise BizException(
            message="用户token已失效，请重新登录", code=ResponseCode.UNAUTHORIZED
        ) from exc
