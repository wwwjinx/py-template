from typing import Annotated

from fastapi import APIRouter, Depends

from app.db import SessionDep
from app.deps import CurrentUserDep, require_permissions
from app.router.system.dict import service
from app.schemas.dict import (
    DictDataCreate,
    DictDataQuery,
    DictDataUpdate,
    DictTypeCreate,
    DictTypeQuery,
    DictTypeUpdate,
)

router = APIRouter(prefix="/system/dict", tags=["系统管理-字典管理"])


@router.get("/type/list", dependencies=[require_permissions("system:dict:list")])
async def list_types(
    db: SessionDep, current: CurrentUserDep, query: Annotated[DictTypeQuery, Depends()]
):
    return await service.list_types(db, query)


@router.get(
    "/type/optionselect",
    dependencies=[require_permissions("system:dict:query", "system:dict:list")],
)
async def option_types(db: SessionDep, current: CurrentUserDep):
    return await service.option_types(db)


@router.post("/type", dependencies=[require_permissions("system:dict:add")])
async def create_type(payload: DictTypeCreate, db: SessionDep, current: CurrentUserDep):
    return await service.create_type(db, payload, current)


@router.put("/type", dependencies=[require_permissions("system:dict:edit")])
async def update_type(payload: DictTypeUpdate, db: SessionDep, current: CurrentUserDep):
    return await service.update_type(db, payload, current)


@router.get("/type/{dict_id}", dependencies=[require_permissions("system:dict:query")])
async def get_type(dict_id: int, db: SessionDep, current: CurrentUserDep):
    return await service.get_type(db, dict_id)


@router.delete("/type/{dict_ids}", dependencies=[require_permissions("system:dict:remove")])
async def delete_types(dict_ids: str, db: SessionDep, current: CurrentUserDep):
    return await service.delete_types(db, dict_ids, current)


@router.get("/data/type/{dict_type}")
async def list_data_by_type(dict_type: str, db: SessionDep, current: CurrentUserDep):
    """按类型取字典，前端 useDict 会用；登录即可。"""
    return await service.list_data_by_type(db, dict_type)


@router.get("/data/list", dependencies=[require_permissions("system:dict:list")])
async def list_data(
    db: SessionDep, current: CurrentUserDep, query: Annotated[DictDataQuery, Depends()]
):
    return await service.list_data(db, query)


@router.post("/data", dependencies=[require_permissions("system:dict:add")])
async def create_data(payload: DictDataCreate, db: SessionDep, current: CurrentUserDep):
    return await service.create_data(db, payload, current)


@router.put("/data", dependencies=[require_permissions("system:dict:edit")])
async def update_data(payload: DictDataUpdate, db: SessionDep, current: CurrentUserDep):
    return await service.update_data(db, payload, current)


@router.get("/data/{dict_code}", dependencies=[require_permissions("system:dict:query")])
async def get_data(dict_code: int, db: SessionDep, current: CurrentUserDep):
    return await service.get_data(db, dict_code)


@router.delete("/data/{dict_codes}", dependencies=[require_permissions("system:dict:remove")])
async def delete_data(dict_codes: str, db: SessionDep, current: CurrentUserDep):
    return await service.delete_data(db, dict_codes, current)
