from app.db import check_db
from app.enums import ResponseCode
from app.redis_client import check_redis
from app.utils.result import Result


def ping() -> Result:
    return Result.ok(data={"ok": True})


def db() -> Result:
    status = check_db()
    if status.get("ok"):
        return Result.ok(data=status)
    return Result.fail(
        msg=status.get("error") or "database unavailable",
        code=ResponseCode.SERVER_ERROR,
        data=status,
    )


def redis() -> Result:
    status = check_redis()
    if status.get("ok"):
        return Result.ok(data=status)
    return Result.fail(
        msg=status.get("error") or "redis unavailable",
        code=ResponseCode.SERVER_ERROR,
        data=status,
    )
