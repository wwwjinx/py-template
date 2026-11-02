from __future__ import annotations

from fastapi import APIRouter

from app.db import check_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/health/db")
async def health_db():
    return check_db()
