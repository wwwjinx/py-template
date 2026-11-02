from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/xx")
async def test_xx():
    return {"ok": True, "path": "xx"}


@router.get("/{name}")
async def test_name(name: str):
    return {"ok": True, "path": name}
