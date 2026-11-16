"""用户管理。"""

from datetime import UTC, datetime

from sqlalchemy import func
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.constants import ADMIN_USER_ID, DEL_FLAG_DELETED, DEL_FLAG_NORMAL
from app.core.exceptions import BizException
from app.enums import ResponseCode, ResponseMsg
from app.models.system import SysDept, SysRole, SysUser, SysUserRole
from app.schemas.common import dump_camel, page_data, parse_ids
from app.schemas.login import CurrentUserOut
from app.schemas.role import RoleOut
from app.schemas.user import (
    ResetPwdBody,
    UserCreate,
    UserOut,
    UserQuery,
    UserStatusBody,
    UserUpdate,
)
from app.utils.password import hash_password
from app.utils.result import Result


def _now() -> datetime:
    return datetime.now(UTC)


def _is_admin(user_id: int | None) -> bool:
    return user_id == ADMIN_USER_ID


async def _replace_user_roles(db: AsyncSession, user_id: int, role_ids: list[int] | None) -> None:
    existing = (await db.exec(select(SysUserRole).where(SysUserRole.user_id == user_id))).all()
    for row in existing:
        await db.delete(row)
    for role_id in role_ids or []:
        if role_id == 1 and user_id != ADMIN_USER_ID:
            # 非超管用户不能分配超管角色
            raise BizException(message="不允许分配超级管理员角色", code=ResponseCode.FORBIDDEN)
        db.add(SysUserRole(user_id=user_id, role_id=role_id))


async def _to_out(db: AsyncSession, user: SysUser, *, with_roles: bool = False) -> dict:
    out = UserOut.model_validate(user)
    out.admin = _is_admin(user.user_id)
    if user.dept_id:
        dept = await db.get(SysDept, user.dept_id)
        if dept and dept.del_flag == DEL_FLAG_NORMAL:
            out.dept = {"deptId": dept.dept_id, "deptName": dept.dept_name}
    if with_roles and user.user_id is not None:
        roles = (
            await db.exec(
                select(SysRole)
                .join(SysUserRole, col(SysUserRole.role_id) == col(SysRole.role_id))
                .where(SysUserRole.user_id == user.user_id, SysRole.del_flag == DEL_FLAG_NORMAL)
            )
        ).all()
        out.roles = [dump_camel(RoleOut.model_validate(r)) for r in roles]
        out.role_ids = [r.role_id for r in roles if r.role_id is not None]
    return dump_camel(out)


async def list_users(db: AsyncSession, query: UserQuery) -> Result:
    filters = [SysUser.del_flag == DEL_FLAG_NORMAL]
    if query.user_name:
        filters.append(col(SysUser.user_name).contains(query.user_name))
    if query.phonenumber:
        filters.append(col(SysUser.phonenumber).contains(query.phonenumber))
    if query.status:
        filters.append(SysUser.status == query.status)
    if query.dept_id:
        filters.append(SysUser.dept_id == query.dept_id)

    total = (await db.exec(select(func.count()).select_from(SysUser).where(*filters))).one()
    rows = (
        await db.exec(
            select(SysUser)
            .where(*filters)
            .order_by(col(SysUser.user_id))
            .offset((query.page_num - 1) * query.page_size)
            .limit(query.page_size)
        )
    ).all()
    return Result.ok(data=page_data([await _to_out(db, u) for u in rows], int(total)))


async def get_user(db: AsyncSession, user_id: int) -> Result:
    user = await db.get(SysUser, user_id)
    if user is None or user.del_flag != DEL_FLAG_NORMAL:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    return Result.ok(data=await _to_out(db, user, with_roles=True))


async def option_roles(db: AsyncSession) -> Result:
    roles = (
        await db.exec(
            select(SysRole)
            .where(SysRole.del_flag == DEL_FLAG_NORMAL)
            .order_by(col(SysRole.role_sort))
        )
    ).all()
    return Result.ok(data={"roles": [dump_camel(RoleOut.model_validate(r)) for r in roles]})


async def create_user(db: AsyncSession, payload: UserCreate, current: CurrentUserOut) -> Result:
    exists = (
        await db.exec(
            select(SysUser).where(
                SysUser.user_name == payload.user_name, SysUser.del_flag == DEL_FLAG_NORMAL
            )
        )
    ).first()
    if exists:
        raise BizException(
            message=f"登录账号已存在：{payload.user_name}", code=ResponseCode.PARAM_ERROR
        )
    user = SysUser(
        user_name=payload.user_name,
        nick_name=payload.nick_name,
        password=hash_password(payload.password),
        dept_id=payload.dept_id,
        email=payload.email or "",
        phonenumber=payload.phonenumber or "",
        sex=payload.sex or "0",
        status=payload.status or "0",
        remark=payload.remark,
        time_zone="auto",
        pwd_update_date=_now(),
        create_by=current.user.user_name,
        create_time=_now(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    await _replace_user_roles(db, user.user_id, payload.role_ids)
    await db.commit()
    return Result.ok(data=await _to_out(db, user, with_roles=True), msg="新增成功")


async def update_user(db: AsyncSession, payload: UserUpdate, current: CurrentUserOut) -> Result:
    user = await db.get(SysUser, payload.user_id)
    if user is None or user.del_flag != DEL_FLAG_NORMAL:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    data = payload.model_dump(exclude={"user_id", "role_ids"}, exclude_none=True)
    for key, value in data.items():
        setattr(user, key, value)
    user.update_by = current.user.user_name
    user.update_time = _now()
    db.add(user)
    if payload.role_ids is not None:
        if _is_admin(user.user_id) and 1 not in payload.role_ids:
            raise BizException(message="不允许取消超级管理员角色", code=ResponseCode.FORBIDDEN)
        await _replace_user_roles(db, user.user_id, payload.role_ids)
    await db.commit()
    await db.refresh(user)
    return Result.ok(data=await _to_out(db, user, with_roles=True), msg="修改成功")


async def delete_users(db: AsyncSession, user_ids: str, current: CurrentUserOut) -> Result:
    ids = parse_ids(user_ids)
    if not ids:
        raise BizException(message=ResponseMsg.PARAM_ERROR, code=ResponseCode.PARAM_ERROR)
    if ADMIN_USER_ID in ids:
        raise BizException(message="不允许删除超级管理员", code=ResponseCode.FORBIDDEN)
    if current.user.user_id in ids:
        raise BizException(message="不能删除当前用户", code=ResponseCode.FORBIDDEN)
    for user_id in ids:
        user = await db.get(SysUser, user_id)
        if user is None or user.del_flag != DEL_FLAG_NORMAL:
            continue
        user.del_flag = DEL_FLAG_DELETED
        user.update_by = current.user.user_name
        user.update_time = _now()
        db.add(user)
    await db.commit()
    return Result.ok(msg="删除成功")


async def reset_pwd(db: AsyncSession, payload: ResetPwdBody, current: CurrentUserOut) -> Result:
    user = await db.get(SysUser, payload.user_id)
    if user is None or user.del_flag != DEL_FLAG_NORMAL:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    user.password = hash_password(payload.password)
    user.pwd_update_date = _now()
    user.update_by = current.user.user_name
    user.update_time = _now()
    db.add(user)
    await db.commit()
    return Result.ok(msg="重置成功")


async def change_status(
    db: AsyncSession, payload: UserStatusBody, current: CurrentUserOut
) -> Result:
    if _is_admin(payload.user_id):
        raise BizException(message="不允许停用超级管理员", code=ResponseCode.FORBIDDEN)
    user = await db.get(SysUser, payload.user_id)
    if user is None or user.del_flag != DEL_FLAG_NORMAL:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    user.status = payload.status
    user.update_by = current.user.user_name
    user.update_time = _now()
    db.add(user)
    await db.commit()
    return Result.ok(msg="修改成功")
