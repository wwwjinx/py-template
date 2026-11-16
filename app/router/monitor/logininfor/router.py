from typing import Annotated

from fastapi import APIRouter, Depends

from app.db import SessionDep
from app.deps import CurrentUserDep, require_permissions
from app.router.monitor.logininfor import service
from app.schemas.log import LoginLogQuery

router = APIRouter(prefix="/monitor/logininfor", tags=["系统监控-登录日志"])


@router.get("/list", dependencies=[require_permissions("monitor:logininfor:list")])
async def list_logs(
    db: SessionDep, current: CurrentUserDep, query: Annotated[LoginLogQuery, Depends()]
):
    return await service.list_logs(db, query)


@router.delete("/clean", dependencies=[require_permissions("monitor:logininfor:remove")])
async def clean_logs(db: SessionDep, current: CurrentUserDep):
    return await service.clean_logs(db)


@router.delete("/{info_ids}", dependencies=[require_permissions("monitor:logininfor:remove")])
async def delete_logs(info_ids: str, db: SessionDep, current: CurrentUserDep):
    return await service.delete_logs(db, info_ids)
