"""部门管理。"""

from datetime import UTC, datetime

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.constants import DEL_FLAG_DELETED, DEL_FLAG_NORMAL, MENU_ROOT_ID
from app.core.exceptions import BizException
from app.enums import ResponseCode, ResponseMsg
from app.models.system import SysDept, SysUser
from app.schemas.common import dump_camel, parse_ids
from app.schemas.dept import DeptCreate, DeptOut, DeptQuery, DeptUpdate
from app.schemas.login import CurrentUserOut
from app.utils.result import Result


def _now() -> datetime:
    return datetime.now(UTC)


def _build_tree(nodes: list[DeptOut], pid: int = MENU_ROOT_ID) -> list[dict]:
    tree: list[dict] = []
    for node in nodes:
        if (node.parent_id or 0) == pid:
            item = dump_camel(node)
            children = _build_tree(nodes, node.dept_id)
            if children:
                item["children"] = children
            tree.append(item)
    return tree


async def _ancestors_of(db: AsyncSession, parent_id: int) -> str:
    if not parent_id:
        return "0"
    parent = await db.get(SysDept, parent_id)
    if parent is None or parent.del_flag != DEL_FLAG_NORMAL:
        raise BizException(message="上级部门不存在", code=ResponseCode.PARAM_ERROR)
    prefix = parent.ancestors or "0"
    return f"{prefix},{parent.dept_id}"


async def list_depts(db: AsyncSession, query: DeptQuery, *, as_tree: bool = False) -> Result:
    stmt = select(SysDept).where(SysDept.del_flag == DEL_FLAG_NORMAL)
    if query.dept_name:
        stmt = stmt.where(col(SysDept.dept_name).contains(query.dept_name))
    if query.status:
        stmt = stmt.where(SysDept.status == query.status)
    rows = (await db.exec(stmt.order_by(col(SysDept.parent_id), col(SysDept.order_num)))).all()
    outs = [DeptOut.model_validate(r) for r in rows]
    if as_tree:
        return Result.ok(data=_build_tree(outs))
    return Result.ok(data=[dump_camel(o) for o in outs])


async def get_dept(db: AsyncSession, dept_id: int) -> Result:
    dept = await db.get(SysDept, dept_id)
    if dept is None or dept.del_flag != DEL_FLAG_NORMAL:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    return Result.ok(data=dump_camel(DeptOut.model_validate(dept)))


async def create_dept(db: AsyncSession, payload: DeptCreate, current: CurrentUserOut) -> Result:
    dept = SysDept(
        parent_id=payload.parent_id,
        ancestors=await _ancestors_of(db, payload.parent_id),
        dept_name=payload.dept_name,
        order_num=payload.order_num,
        leader=payload.leader,
        phone=payload.phone,
        email=payload.email,
        status=payload.status or "0",
        create_by=current.user.user_name,
        create_time=_now(),
    )
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return Result.ok(data=dump_camel(DeptOut.model_validate(dept)), msg="新增成功")


async def update_dept(db: AsyncSession, payload: DeptUpdate, current: CurrentUserOut) -> Result:
    dept = await db.get(SysDept, payload.dept_id)
    if dept is None or dept.del_flag != DEL_FLAG_NORMAL:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    if payload.parent_id == payload.dept_id:
        raise BizException(message="上级部门不能选择自己", code=ResponseCode.PARAM_ERROR)
    old_ancestors = dept.ancestors or "0"
    new_ancestors = await _ancestors_of(db, payload.parent_id)
    data = payload.model_dump(exclude={"dept_id"}, exclude_none=True)
    for key, value in data.items():
        setattr(dept, key, value)
    dept.ancestors = new_ancestors
    dept.update_by = current.user.user_name
    dept.update_time = _now()
    db.add(dept)
    # 同步更新子孙 ancestors
    children = (
        await db.exec(
            select(SysDept).where(
                SysDept.del_flag == DEL_FLAG_NORMAL,
                col(SysDept.ancestors).contains(f",{dept.dept_id}"),
            )
        )
    ).all()
    old_prefix = f"{old_ancestors},{dept.dept_id}"
    new_prefix = f"{new_ancestors},{dept.dept_id}"
    for child in children:
        if child.ancestors and child.ancestors.startswith(old_prefix):
            child.ancestors = new_prefix + child.ancestors[len(old_prefix) :]
            db.add(child)
    await db.commit()
    await db.refresh(dept)
    return Result.ok(data=dump_camel(DeptOut.model_validate(dept)), msg="修改成功")


async def delete_depts(db: AsyncSession, dept_ids: str, current: CurrentUserOut) -> Result:
    ids = parse_ids(dept_ids)
    if not ids:
        raise BizException(message=ResponseMsg.PARAM_ERROR, code=ResponseCode.PARAM_ERROR)
    for dept_id in ids:
        child = (
            await db.exec(
                select(SysDept).where(
                    SysDept.parent_id == dept_id, SysDept.del_flag == DEL_FLAG_NORMAL
                )
            )
        ).first()
        if child:
            raise BizException(message="存在下级部门，不允许删除", code=ResponseCode.PARAM_ERROR)
        user = (
            await db.exec(
                select(SysUser).where(
                    SysUser.dept_id == dept_id, SysUser.del_flag == DEL_FLAG_NORMAL
                )
            )
        ).first()
        if user:
            raise BizException(message="部门存在用户，不允许删除", code=ResponseCode.PARAM_ERROR)
        dept = await db.get(SysDept, dept_id)
        if dept is None or dept.del_flag != DEL_FLAG_NORMAL:
            continue
        dept.del_flag = DEL_FLAG_DELETED
        db.add(dept)
    await db.commit()
    return Result.ok(msg="删除成功")
