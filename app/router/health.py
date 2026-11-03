from __future__ import annotations

from fastapi import APIRouter

from app.db import check_db
from app.enums import ErrorCode
from app.redis_client import check_redis
from app.utils.result import Result

router = APIRouter(tags=["health"], prefix="/health")


@router.get("")
async def health():
    return Result.ok(data={"ok": True})


@router.get("/db")
async def health_db():
    status = check_db()
    if status.get("ok"):
        return Result.ok(data=status)
    return Result.fail(
        message=status.get("error") or "database unavailable",
        code=ErrorCode.SERVER_ERROR,
        data=status,
    )


@router.get("/redis")
async def health_redis():
    status = check_redis()
    if status.get("ok"):
        return Result.ok(data=status)
    return Result.fail(
        message=status.get("error") or "redis unavailable",
        code=ErrorCode.SERVER_ERROR,
        data=status,
    )
