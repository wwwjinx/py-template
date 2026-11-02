from __future__ import annotations

from fastapi import APIRouter

from app.router import health, test

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(test.router)

__all__ = ["api_router"]
