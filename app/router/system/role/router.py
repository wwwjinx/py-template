from typing import Annotated

from fastapi import APIRouter, Depends

from app.db import SessionDep
from app.deps import CurrentUserDep, require_permissions
from app.router.system.role import service
from app.schemas.role import RoleCreate, RoleQuery, RoleStatusBody, RoleUpdate

router = APIRouter(prefix="/system/role", tags=["系统管理-角色管理"])


@router.get("/list", dependencies=[require_permissions("system:role:list")])
async def list_roles(
    db: SessionDep, current: CurrentUserDep, query: Annotated[RoleQuery, Depends()]
):
    return await service.list_roles(db, query)


@router.post("/", dependencies=[require_permissions("system:role:add")])
async def create_role(payload: RoleCreate, db: SessionDep, current: CurrentUserDep):
    return await service.create_role(db, payload, current)


@router.put("/", dependencies=[require_permissions("system:role:edit")])
async def update_role(payload: RoleUpdate, db: SessionDep, current: CurrentUserDep):
    return await service.update_role(db, payload, current)


@router.put("/changeStatus", dependencies=[require_permissions("system:role:edit")])
async def change_status(payload: RoleStatusBody, db: SessionDep, current: CurrentUserDep):
    return await service.change_status(db, payload, current)


@router.get("/{role_id}", dependencies=[require_permissions("system:role:query")])
async def get_role(role_id: int, db: SessionDep, current: CurrentUserDep):
    return await service.get_role(db, role_id)


@router.delete("/{role_ids}", dependencies=[require_permissions("system:role:remove")])
async def delete_roles(role_ids: str, db: SessionDep, current: CurrentUserDep):
    return await service.delete_roles(db, role_ids, current)
