from typing import Annotated

from fastapi import APIRouter, Depends

from app.db import SessionDep
from app.deps import CurrentUserDep, require_permissions
from app.router.system.menu import service
from app.schemas.menu import MenuCreate, MenuQuery, MenuUpdate

router = APIRouter(prefix="/system/menu", tags=["系统管理-菜单管理"])


@router.get(
    "/treeselect", dependencies=[require_permissions("system:menu:list", "system:menu:query")]
)
async def tree_select(db: SessionDep, current: CurrentUserDep):
    return await service.tree_select(db)


@router.get(
    "/roleMenuTreeselect/{role_id}",
    dependencies=[require_permissions("system:menu:query", "system:role:query")],
)
async def role_menu_tree(role_id: int, db: SessionDep, current: CurrentUserDep):
    return await service.role_menu_tree(db, role_id)


@router.get("/list", dependencies=[require_permissions("system:menu:list")])
async def list_menus(
    db: SessionDep, current: CurrentUserDep, query: Annotated[MenuQuery, Depends()]
):
    return await service.list_menus(db, query)


@router.post("/", dependencies=[require_permissions("system:menu:add")])
async def create_menu(payload: MenuCreate, db: SessionDep, current: CurrentUserDep):
    return await service.create_menu(db, payload, current)


@router.put("/", dependencies=[require_permissions("system:menu:edit")])
async def update_menu(payload: MenuUpdate, db: SessionDep, current: CurrentUserDep):
    return await service.update_menu(db, payload, current)


@router.get("/{menu_id}", dependencies=[require_permissions("system:menu:query")])
async def get_menu(menu_id: int, db: SessionDep, current: CurrentUserDep):
    return await service.get_menu(db, menu_id)


@router.delete("/{menu_ids}", dependencies=[require_permissions("system:menu:remove")])
async def delete_menus(menu_ids: str, db: SessionDep, current: CurrentUserDep):
    return await service.delete_menus(db, menu_ids, current)
