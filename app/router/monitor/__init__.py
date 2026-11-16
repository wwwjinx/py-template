from fastapi import APIRouter

from app.router.monitor import logininfor, operlog

router = APIRouter()
router.include_router(operlog.router)
router.include_router(logininfor.router)

__all__ = ["router"]
