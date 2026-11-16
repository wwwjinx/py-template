from typing import Annotated

from fastapi import APIRouter, Depends

from app.db import SessionDep
from app.deps import CurrentUserDep, require_permissions
from app.router.system.dept import service
from app.schemas.dept import DeptCreate, DeptQuery, DeptUpdate

router = APIRouter(prefix="/system/dept", tags=["系统管理-部门管理"])


@router.get("/list", dependencies=[require_permissions("system:dept:list")])
async def list_depts(
    db: SessionDep, current: CurrentUserDep, query: Annotated[DeptQuery, Depends()]
):
    return await service.list_depts(db, query, as_tree=False)


@router.get(
    "/treeselect", dependencies=[require_permissions("system:dept:list", "system:user:list")]
)
async def tree_select(
    db: SessionDep, current: CurrentUserDep, query: Annotated[DeptQuery, Depends()]
):
    return await service.list_depts(db, query, as_tree=True)


@router.post("/", dependencies=[require_permissions("system:dept:add")])
async def create_dept(payload: DeptCreate, db: SessionDep, current: CurrentUserDep):
    return await service.create_dept(db, payload, current)


@router.put("/", dependencies=[require_permissions("system:dept:edit")])
async def update_dept(payload: DeptUpdate, db: SessionDep, current: CurrentUserDep):
    return await service.update_dept(db, payload, current)


@router.get("/{dept_id}", dependencies=[require_permissions("system:dept:query")])
async def get_dept(dept_id: int, db: SessionDep, current: CurrentUserDep):
    return await service.get_dept(db, dept_id)


@router.delete("/{dept_ids}", dependencies=[require_permissions("system:dept:remove")])
async def delete_depts(dept_ids: str, db: SessionDep, current: CurrentUserDep):
    return await service.delete_depts(db, dept_ids, current)
