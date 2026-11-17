from fastapi import APIRouter, Depends

from app.deps import get_current_user
from app.router import common, health, login, monitor, system, test
from app.router.root import router as root_router

# 未登录可访问。新增公开接口必须登记到这里，其余一律走 api_router。
public_router = APIRouter()
public_router.include_router(root_router)
public_router.include_router(health.router)
public_router.include_router(login.public_router)

# 默认全鉴权：router 级依赖覆盖所有子路由，新增模块 include 进来就不会漏鉴权。
# 权限点（require_permissions）仍由各接口自己声明。
api_router = APIRouter(dependencies=[Depends(get_current_user)])
api_router.include_router(login.router)
api_router.include_router(system.router)
api_router.include_router(monitor.router)
api_router.include_router(test.router)
api_router.include_router(common.router)

__all__ = ["api_router", "public_router"]
