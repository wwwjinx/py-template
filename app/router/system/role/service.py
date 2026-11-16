"""角色管理。"""

from datetime import UTC, datetime

from sqlalchemy import func
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.constants import ADMIN_ROLE_ID, DEL_FLAG_DELETED, DEL_FLAG_NORMAL
from app.core.exceptions import BizException
from app.enums import ResponseCode, ResponseMsg
from app.models.system import SysRole, SysRoleMenu, SysUserRole
from app.schemas.common import dump_camel, page_data, parse_ids
from app.schemas.login import CurrentUserOut
from app.schemas.role import RoleCreate, RoleOut, RoleQuery, RoleStatusBody, RoleUpdate
from app.utils.result import Result


def _now() -> datetime:
    return datetime.now(UTC)


async def _menu_ids_of(db: AsyncSession, role_id: int) -> list[int]:
    rows = (await db.exec(select(SysRoleMenu).where(SysRoleMenu.role_id == role_id))).all()
    return [r.menu_id for r in rows]


async def _replace_role_menus(db: AsyncSession, role_id: int, menu_ids: list[int] | None) -> None:
    existing = (await db.exec(select(SysRoleMenu).where(SysRoleMenu.role_id == role_id))).all()
    for row in existing:
        await db.delete(row)
    for menu_id in menu_ids or []:
        db.add(SysRoleMenu(role_id=role_id, menu_id=menu_id))


async def list_roles(db: AsyncSession, query: RoleQuery) -> Result:
    filters = [SysRole.del_flag == DEL_FLAG_NORMAL]
    if query.role_name:
        filters.append(col(SysRole.role_name).contains(query.role_name))
    if query.role_key:
        filters.append(col(SysRole.role_key).contains(query.role_key))
    if query.status:
        filters.append(SysRole.status == query.status)
    total = (await db.exec(select(func.count()).select_from(SysRole).where(*filters))).one()
    rows = (
        await db.exec(
            select(SysRole)
            .where(*filters)
            .order_by(col(SysRole.role_sort), col(SysRole.role_id))
            .offset((query.page_num - 1) * query.page_size)
            .limit(query.page_size)
        )
    ).all()
    return Result.ok(
        data=page_data([dump_camel(RoleOut.model_validate(r)) for r in rows], int(total))
    )


async def get_role(db: AsyncSession, role_id: int) -> Result:
    role = await db.get(SysRole, role_id)
    if role is None or role.del_flag != DEL_FLAG_NORMAL:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    out = RoleOut.model_validate(role)
    out.menu_ids = await _menu_ids_of(db, role_id)
    return Result.ok(data=dump_camel(out))


async def create_role(db: AsyncSession, payload: RoleCreate, current: CurrentUserOut) -> Result:
    exists = (
        await db.exec(
            select(SysRole).where(
                SysRole.del_flag == DEL_FLAG_NORMAL,
                (col(SysRole.role_name) == payload.role_name)
                | (col(SysRole.role_key) == payload.role_key),
            )
        )
    ).first()
    if exists:
        raise BizException(message="角色名称或权限字符已存在", code=ResponseCode.PARAM_ERROR)
    role = SysRole(
        role_name=payload.role_name,
        role_key=payload.role_key,
        role_sort=payload.role_sort,
        status=payload.status,
        remark=payload.remark,
        data_scope=payload.data_scope or "1",
        menu_check_strictly=payload.menu_check_strictly
        if payload.menu_check_strictly is not None
        else 1,
        dept_check_strictly=payload.dept_check_strictly
        if payload.dept_check_strictly is not None
        else 1,
        create_by=current.user.user_name,
        create_time=_now(),
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    await _replace_role_menus(db, role.role_id, payload.menu_ids)
    await db.commit()
    return Result.ok(data=dump_camel(RoleOut.model_validate(role)), msg="新增成功")


async def update_role(db: AsyncSession, payload: RoleUpdate, current: CurrentUserOut) -> Result:
    role = await db.get(SysRole, payload.role_id)
    if role is None or role.del_flag != DEL_FLAG_NORMAL:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    data = payload.model_dump(exclude={"role_id", "menu_ids"}, exclude_none=True)
    for key, value in data.items():
        setattr(role, key, value)
    role.update_by = current.user.user_name
    role.update_time = _now()
    db.add(role)
    if payload.menu_ids is not None:
        await _replace_role_menus(db, role.role_id, payload.menu_ids)
    await db.commit()
    await db.refresh(role)
    return Result.ok(msg="修改成功")


async def delete_roles(db: AsyncSession, role_ids: str, current: CurrentUserOut) -> Result:
    ids = parse_ids(role_ids)
    if not ids:
        raise BizException(message=ResponseMsg.PARAM_ERROR, code=ResponseCode.PARAM_ERROR)
    if ADMIN_ROLE_ID in ids:
        raise BizException(message="不允许删除超级管理员角色", code=ResponseCode.FORBIDDEN)
    for role_id in ids:
        assigned = (
            await db.exec(select(SysUserRole).where(SysUserRole.role_id == role_id))
        ).first()
        if assigned:
            role = await db.get(SysRole, role_id)
            name = role.role_name if role else str(role_id)
            raise BizException(
                message=f"角色已分配，不能删除：{name}", code=ResponseCode.PARAM_ERROR
            )
        role = await db.get(SysRole, role_id)
        if role is None or role.del_flag != DEL_FLAG_NORMAL:
            continue
        role.del_flag = DEL_FLAG_DELETED
        role.update_by = current.user.user_name
        role.update_time = _now()
        db.add(role)
    await db.commit()
    return Result.ok(msg="删除成功")


async def change_status(
    db: AsyncSession, payload: RoleStatusBody, current: CurrentUserOut
) -> Result:
    if payload.role_id == ADMIN_ROLE_ID:
        raise BizException(message="不允许停用超级管理员角色", code=ResponseCode.FORBIDDEN)
    role = await db.get(SysRole, payload.role_id)
    if role is None or role.del_flag != DEL_FLAG_NORMAL:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    role.status = payload.status
    role.update_by = current.user.user_name
    role.update_time = _now()
    db.add(role)
    await db.commit()
    return Result.ok(msg="修改成功")
