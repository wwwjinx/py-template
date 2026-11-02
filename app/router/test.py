from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.exceptions import BizException
from app.utils.result import Result

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/xx")
async def test_xx():
    return Result.ok(data={"ok": True, "path": "/test/xx"})


@router.get("/err")
async def test_err():
    """Demo: business error → Result.fail (HTTP 200, body.code=501)."""
    raise BizException(message="test error", code=501)


@router.get("/http-err")
async def test_http_err():
    """Demo: HTTPException also wrapped into Result (HTTP 200, body.code)."""
    raise HTTPException(status_code=401, detail="unauthorized")


@router.get("/{name}")
async def test_name(name: str):
    return Result.ok(data={"ok": True, "path": f"/test/{name}"})
