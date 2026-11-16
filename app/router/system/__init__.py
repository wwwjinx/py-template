from fastapi import APIRouter

from app.router.system import dept, dict, menu, role, user

router = APIRouter()
router.include_router(user.router)
router.include_router(role.router)
router.include_router(menu.router)
router.include_router(dept.router)
router.include_router(dict.router)

__all__ = ["router"]
