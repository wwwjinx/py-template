from fastapi import APIRouter

from app.router import health, login, monitor, system, test
from app.router.root import router as root_router

api_router = APIRouter()
api_router.include_router(root_router)
api_router.include_router(health.router)
api_router.include_router(login.router)
api_router.include_router(system.router)
api_router.include_router(monitor.router)
api_router.include_router(test.router)

__all__ = ["api_router"]
