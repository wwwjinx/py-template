"""字典类型与字典数据。"""

from datetime import UTC, datetime

from sqlalchemy import func
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import BizException
from app.enums import ResponseCode, ResponseMsg
from app.models.system import SysDictData, SysDictType
from app.schemas.common import dump_camel, page_data, parse_ids
from app.schemas.dict import (
    DictDataCreate,
    DictDataOut,
    DictDataQuery,
    DictDataUpdate,
    DictTypeCreate,
    DictTypeOut,
    DictTypeQuery,
    DictTypeUpdate,
)
from app.schemas.login import CurrentUserOut
from app.utils.result import Result


def _now() -> datetime:
    return datetime.now(UTC)


async def list_types(db: AsyncSession, query: DictTypeQuery) -> Result:
    filters = []
    if query.dict_name:
        filters.append(col(SysDictType.dict_name).contains(query.dict_name))
    if query.dict_type:
        filters.append(col(SysDictType.dict_type).contains(query.dict_type))
    if query.status:
        filters.append(SysDictType.status == query.status)
    stmt = select(SysDictType)
    count_stmt = select(func.count()).select_from(SysDictType)
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = (await db.exec(count_stmt)).one()
    rows = (
        await db.exec(
            stmt.order_by(col(SysDictType.dict_id))
            .offset((query.page_num - 1) * query.page_size)
            .limit(query.page_size)
        )
    ).all()
    return Result.ok(
        data=page_data([dump_camel(DictTypeOut.model_validate(r)) for r in rows], int(total))
    )


async def option_types(db: AsyncSession) -> Result:
    rows = (await db.exec(select(SysDictType).order_by(col(SysDictType.dict_id)))).all()
    return Result.ok(data=[dump_camel(DictTypeOut.model_validate(r)) for r in rows])


async def get_type(db: AsyncSession, dict_id: int) -> Result:
    row = await db.get(SysDictType, dict_id)
    if row is None:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    return Result.ok(data=dump_camel(DictTypeOut.model_validate(row)))


async def create_type(db: AsyncSession, payload: DictTypeCreate, current: CurrentUserOut) -> Result:
    exists = (
        await db.exec(select(SysDictType).where(SysDictType.dict_type == payload.dict_type))
    ).first()
    if exists:
        raise BizException(
            message=f"字典类型已存在：{payload.dict_type}", code=ResponseCode.PARAM_ERROR
        )
    row = SysDictType(
        **payload.model_dump(),
        create_by=current.user.user_name,
        create_time=_now(),
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return Result.ok(data=dump_camel(DictTypeOut.model_validate(row)), msg="新增成功")


async def update_type(db: AsyncSession, payload: DictTypeUpdate, current: CurrentUserOut) -> Result:
    row = await db.get(SysDictType, payload.dict_id)
    if row is None:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    old_type = row.dict_type
    data = payload.model_dump(exclude={"dict_id"}, exclude_none=True)
    if payload.dict_type != old_type:
        exists = (
            await db.exec(select(SysDictType).where(SysDictType.dict_type == payload.dict_type))
        ).first()
        if exists:
            raise BizException(
                message=f"字典类型已存在：{payload.dict_type}", code=ResponseCode.PARAM_ERROR
            )
    for key, value in data.items():
        setattr(row, key, value)
    row.update_by = current.user.user_name
    row.update_time = _now()
    db.add(row)
    if payload.dict_type != old_type:
        datas = (await db.exec(select(SysDictData).where(SysDictData.dict_type == old_type))).all()
        for item in datas:
            item.dict_type = payload.dict_type
            db.add(item)
    await db.commit()
    await db.refresh(row)
    return Result.ok(data=dump_camel(DictTypeOut.model_validate(row)), msg="修改成功")


async def delete_types(db: AsyncSession, dict_ids: str, current: CurrentUserOut) -> Result:
    ids = parse_ids(dict_ids)
    if not ids:
        raise BizException(message=ResponseMsg.PARAM_ERROR, code=ResponseCode.PARAM_ERROR)
    for dict_id in ids:
        row = await db.get(SysDictType, dict_id)
        if row is None:
            continue
        datas = (
            await db.exec(select(SysDictData).where(SysDictData.dict_type == row.dict_type))
        ).all()
        for item in datas:
            await db.delete(item)
        await db.delete(row)
    await db.commit()
    return Result.ok(msg="删除成功")


async def list_data(db: AsyncSession, query: DictDataQuery) -> Result:
    filters = []
    if query.dict_type:
        filters.append(SysDictData.dict_type == query.dict_type)
    if query.dict_label:
        filters.append(col(SysDictData.dict_label).contains(query.dict_label))
    if query.status:
        filters.append(SysDictData.status == query.status)
    stmt = select(SysDictData)
    count_stmt = select(func.count()).select_from(SysDictData)
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = (await db.exec(count_stmt)).one()
    rows = (
        await db.exec(
            stmt.order_by(col(SysDictData.dict_sort), col(SysDictData.dict_code))
            .offset((query.page_num - 1) * query.page_size)
            .limit(query.page_size)
        )
    ).all()
    return Result.ok(
        data=page_data([dump_camel(DictDataOut.model_validate(r)) for r in rows], int(total))
    )


async def list_data_by_type(db: AsyncSession, dict_type: str) -> Result:
    rows = (
        await db.exec(
            select(SysDictData)
            .where(SysDictData.dict_type == dict_type, SysDictData.status == "0")
            .order_by(col(SysDictData.dict_sort), col(SysDictData.dict_code))
        )
    ).all()
    return Result.ok(data=[dump_camel(DictDataOut.model_validate(r)) for r in rows])


async def get_data(db: AsyncSession, dict_code: int) -> Result:
    row = await db.get(SysDictData, dict_code)
    if row is None:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    return Result.ok(data=dump_camel(DictDataOut.model_validate(row)))


async def create_data(db: AsyncSession, payload: DictDataCreate, current: CurrentUserOut) -> Result:
    row = SysDictData(
        **payload.model_dump(),
        create_by=current.user.user_name,
        create_time=_now(),
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return Result.ok(data=dump_camel(DictDataOut.model_validate(row)), msg="新增成功")


async def update_data(db: AsyncSession, payload: DictDataUpdate, current: CurrentUserOut) -> Result:
    row = await db.get(SysDictData, payload.dict_code)
    if row is None:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    data = payload.model_dump(exclude={"dict_code"}, exclude_none=True)
    for key, value in data.items():
        setattr(row, key, value)
    row.update_by = current.user.user_name
    row.update_time = _now()
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return Result.ok(data=dump_camel(DictDataOut.model_validate(row)), msg="修改成功")


async def delete_data(db: AsyncSession, dict_codes: str, current: CurrentUserOut) -> Result:
    ids = parse_ids(dict_codes)
    if not ids:
        raise BizException(message=ResponseMsg.PARAM_ERROR, code=ResponseCode.PARAM_ERROR)
    for dict_code in ids:
        row = await db.get(SysDictData, dict_code)
        if row is None:
            continue
        await db.delete(row)
    await db.commit()
    return Result.ok(msg="删除成功")
