from typing import Annotated

from fastapi import APIRouter, Depends

from app.db import SessionDep
from app.deps import CurrentUserDep, require_permissions
from app.router.monitor.operlog import service
from app.schemas.log import OperLogQuery

router = APIRouter(prefix="/monitor/operlog", tags=["系统监控-操作日志"])


@router.get("/list", dependencies=[require_permissions("monitor:operlog:list")])
async def list_logs(
    db: SessionDep, current: CurrentUserDep, query: Annotated[OperLogQuery, Depends()]
):
    return await service.list_logs(db, query)


@router.delete("/clean", dependencies=[require_permissions("monitor:operlog:remove")])
async def clean_logs(db: SessionDep, current: CurrentUserDep):
    return await service.clean_logs(db)


@router.delete("/{oper_ids}", dependencies=[require_permissions("monitor:operlog:remove")])
async def delete_logs(oper_ids: str, db: SessionDep, current: CurrentUserDep):
    return await service.delete_logs(db, oper_ids)
