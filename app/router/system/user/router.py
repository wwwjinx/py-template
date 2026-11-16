from typing import Annotated

from fastapi import APIRouter, Depends

from app.db import SessionDep
from app.deps import CurrentUserDep, require_permissions
from app.router.system.user import service
from app.schemas.user import ResetPwdBody, UserCreate, UserQuery, UserStatusBody, UserUpdate

router = APIRouter(prefix="/system/user", tags=["系统管理-用户管理"])


@router.get("/list", dependencies=[require_permissions("system:user:list")])
async def list_users(
    db: SessionDep, current: CurrentUserDep, query: Annotated[UserQuery, Depends()]
):
    return await service.list_users(db, query)


@router.get(
    "/",
    dependencies=[require_permissions("system:user:add", "system:user:edit", "system:user:list")],
)
async def option_roles(db: SessionDep, current: CurrentUserDep):
    return await service.option_roles(db)


@router.post("/", dependencies=[require_permissions("system:user:add")])
async def create_user(payload: UserCreate, db: SessionDep, current: CurrentUserDep):
    return await service.create_user(db, payload, current)


@router.put("/", dependencies=[require_permissions("system:user:edit")])
async def update_user(payload: UserUpdate, db: SessionDep, current: CurrentUserDep):
    return await service.update_user(db, payload, current)


@router.put("/resetPwd", dependencies=[require_permissions("system:user:resetPwd")])
async def reset_pwd(payload: ResetPwdBody, db: SessionDep, current: CurrentUserDep):
    return await service.reset_pwd(db, payload, current)


@router.put("/changeStatus", dependencies=[require_permissions("system:user:edit")])
async def change_status(payload: UserStatusBody, db: SessionDep, current: CurrentUserDep):
    return await service.change_status(db, payload, current)


@router.get("/{user_id}", dependencies=[require_permissions("system:user:query")])
async def get_user(user_id: int, db: SessionDep, current: CurrentUserDep):
    return await service.get_user(db, user_id)


@router.delete("/{user_ids}", dependencies=[require_permissions("system:user:remove")])
async def delete_users(user_ids: str, db: SessionDep, current: CurrentUserDep):
    return await service.delete_users(db, user_ids, current)
