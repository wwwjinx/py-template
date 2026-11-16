"""操作日志查询、删除、清空。"""

from sqlalchemy import delete, func
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import BizException
from app.enums import ResponseCode, ResponseMsg
from app.models.system import SysOperLog
from app.schemas.common import dump_camel, page_data, parse_ids
from app.schemas.log import OperLogOut, OperLogQuery
from app.utils.result import Result


async def list_logs(db: AsyncSession, query: OperLogQuery) -> Result:
    filters = []
    if query.title:
        filters.append(col(SysOperLog.title).contains(query.title))
    if query.oper_name:
        filters.append(col(SysOperLog.oper_name).contains(query.oper_name))
    if query.business_type is not None:
        filters.append(SysOperLog.business_type == query.business_type)
    if query.status is not None:
        filters.append(SysOperLog.status == query.status)
    stmt = select(SysOperLog)
    count_stmt = select(func.count()).select_from(SysOperLog)
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = (await db.exec(count_stmt)).one()
    rows = (
        await db.exec(
            stmt.order_by(col(SysOperLog.oper_id).desc())
            .offset((query.page_num - 1) * query.page_size)
            .limit(query.page_size)
        )
    ).all()
    return Result.ok(
        data=page_data([dump_camel(OperLogOut.model_validate(r)) for r in rows], int(total))
    )


async def delete_logs(db: AsyncSession, oper_ids: str) -> Result:
    ids = parse_ids(oper_ids)
    if not ids:
        raise BizException(message=ResponseMsg.PARAM_ERROR, code=ResponseCode.PARAM_ERROR)
    for oper_id in ids:
        row = await db.get(SysOperLog, oper_id)
        if row is None:
            continue
        await db.delete(row)
    await db.commit()
    return Result.ok(msg="删除成功")


async def clean_logs(db: AsyncSession) -> Result:
    await db.execute(delete(SysOperLog))
    await db.commit()
    return Result.ok(msg="清空成功")
