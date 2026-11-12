from fastapi import HTTPException

from app.core.exceptions import BizException
from app.utils.result import Result


def xx() -> Result:
    return Result.ok(data={"ok": True, "path": "/test/xx"})


def raise_biz() -> None:
    raise BizException(message="test error", code=501)


def raise_http() -> None:
    raise HTTPException(status_code=401, detail="unauthorized")


def by_name(name: str) -> Result:
    return Result.ok(data={"ok": True, "path": f"/test/{name}"})
