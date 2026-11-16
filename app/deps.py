"""登录鉴权依赖。Session 仍由路由注入的 SessionDep 提供，不和 db.py 混在一起。"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import BizException
from app.db import SessionDep
from app.enums import ResponseCode, ResponseMsg
from app.schemas.login import CurrentUserOut
from app.utils.jwt import decode_access_token

_bearer = HTTPBearer(auto_error=False)

ADMIN_USER_ID = 1
ALL_PERMISSION = "*:*:*"


async def get_current_user(
    db: SessionDep,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> CurrentUserOut:
    if creds is None or creds.scheme.lower() != "bearer" or not creds.credentials:
        raise BizException(message=ResponseMsg.UNAUTHORIZED, code=ResponseCode.UNAUTHORIZED)
    payload = decode_access_token(creds.credentials)
    user_id = payload.get("user_id")
    if user_id is None:
        raise BizException(message=ResponseMsg.UNAUTHORIZED, code=ResponseCode.UNAUTHORIZED)
    from app.router.login.service import load_current_user

    return await load_current_user(db, int(user_id))


CurrentUserDep = Annotated[CurrentUserOut, Depends(get_current_user)]


def require_permissions(*perms: str):
    """简单权限检查：超管（permissions 含 *:*:*）直接通过。"""

    async def _checker(current: CurrentUserDep) -> CurrentUserOut:
        if ALL_PERMISSION in current.permissions:
            return current
        if perms and not any(p in current.permissions for p in perms):
            raise BizException(message=ResponseMsg.FORBIDDEN, code=ResponseCode.FORBIDDEN)
        return current

    return Depends(_checker)
