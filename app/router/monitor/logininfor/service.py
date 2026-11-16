"""登录日志查询、删除、清空。"""

from sqlalchemy import delete, func
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import BizException
from app.enums import ResponseCode, ResponseMsg
from app.models.system import SysLogininfor
from app.schemas.common import dump_camel, page_data, parse_ids
from app.schemas.log import LoginLogOut, LoginLogQuery
from app.utils.result import Result


async def list_logs(db: AsyncSession, query: LoginLogQuery) -> Result:
    filters = []
    if query.user_name:
        filters.append(col(SysLogininfor.user_name).contains(query.user_name))
    if query.ipaddr:
        filters.append(col(SysLogininfor.ipaddr).contains(query.ipaddr))
    if query.status:
        filters.append(SysLogininfor.status == query.status)
    stmt = select(SysLogininfor)
    count_stmt = select(func.count()).select_from(SysLogininfor)
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    total = (await db.exec(count_stmt)).one()
    rows = (
        await db.exec(
            stmt.order_by(col(SysLogininfor.info_id).desc())
            .offset((query.page_num - 1) * query.page_size)
            .limit(query.page_size)
        )
    ).all()
    return Result.ok(
        data=page_data([dump_camel(LoginLogOut.model_validate(r)) for r in rows], int(total))
    )


async def delete_logs(db: AsyncSession, info_ids: str) -> Result:
    ids = parse_ids(info_ids)
    if not ids:
        raise BizException(message=ResponseMsg.PARAM_ERROR, code=ResponseCode.PARAM_ERROR)
    for info_id in ids:
        row = await db.get(SysLogininfor, info_id)
        if row is None:
            continue
        await db.delete(row)
    await db.commit()
    return Result.ok(msg="删除成功")


async def clean_logs(db: AsyncSession) -> Result:
    await db.execute(delete(SysLogininfor))
    await db.commit()
    return Result.ok(msg="清空成功")
