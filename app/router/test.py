from __future__ import annotations

from fastapi import APIRouter

from app.utils.result import Result

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/xx")
async def test_xx():
    return Result.ok(data={"ok": True, "path": "/test/xx"})


@router.get("/{name}")
async def test_name(name: str):
    return Result.ok(data={"ok": True, "path": f"/test/{name}"})
