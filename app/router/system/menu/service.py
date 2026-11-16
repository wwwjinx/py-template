"""菜单管理。"""

from datetime import UTC, datetime

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.constants import MENU_ROOT_ID
from app.core.exceptions import BizException
from app.enums import ResponseCode, ResponseMsg
from app.models.system import SysMenu, SysRoleMenu
from app.schemas.common import dump_camel, parse_ids
from app.schemas.login import CurrentUserOut
from app.schemas.menu import MenuCreate, MenuOut, MenuQuery, MenuUpdate
from app.utils.result import Result


def _now() -> datetime:
    return datetime.now(UTC)


def _to_out(menu: SysMenu) -> MenuOut:
    return MenuOut.model_validate(menu)


def _build_tree(nodes: list[MenuOut], pid: int = MENU_ROOT_ID) -> list[dict]:
    tree: list[dict] = []
    for node in nodes:
        if (node.parent_id or 0) == pid:
            item = dump_camel(node)
            children = _build_tree(nodes, node.menu_id)
            if children:
                item["children"] = children
            tree.append(item)
    return tree


async def list_menus(db: AsyncSession, query: MenuQuery) -> Result:
    stmt = select(SysMenu)
    if query.menu_name:
        stmt = stmt.where(col(SysMenu.menu_name).contains(query.menu_name))
    if query.status:
        stmt = stmt.where(SysMenu.status == query.status)
    if query.visible:
        stmt = stmt.where(SysMenu.visible == query.visible)
    rows = (await db.exec(stmt.order_by(col(SysMenu.parent_id), col(SysMenu.order_num)))).all()
    return Result.ok(data=[dump_camel(_to_out(m)) for m in rows])


async def tree_select(db: AsyncSession) -> Result:
    rows = (
        await db.exec(select(SysMenu).order_by(col(SysMenu.parent_id), col(SysMenu.order_num)))
    ).all()
    return Result.ok(data=_build_tree([_to_out(m) for m in rows]))


async def role_menu_tree(db: AsyncSession, role_id: int) -> Result:
    tree = await tree_select(db)
    checked = (
        await db.exec(select(SysRoleMenu.menu_id).where(SysRoleMenu.role_id == role_id))
    ).all()
    return Result.ok(data={"menus": tree.data, "checkedKeys": list(checked)})


async def get_menu(db: AsyncSession, menu_id: int) -> Result:
    menu = await db.get(SysMenu, menu_id)
    if menu is None:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    return Result.ok(data=dump_camel(_to_out(menu)))


async def create_menu(db: AsyncSession, payload: MenuCreate, current: CurrentUserOut) -> Result:
    menu = SysMenu(
        **payload.model_dump(),
        create_by=current.user.user_name,
        create_time=_now(),
    )
    db.add(menu)
    await db.commit()
    await db.refresh(menu)
    return Result.ok(data=dump_camel(_to_out(menu)), msg="新增成功")


async def update_menu(db: AsyncSession, payload: MenuUpdate, current: CurrentUserOut) -> Result:
    menu = await db.get(SysMenu, payload.menu_id)
    if menu is None:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    if payload.parent_id == payload.menu_id:
        raise BizException(message="上级菜单不能选择自己", code=ResponseCode.PARAM_ERROR)
    data = payload.model_dump(exclude={"menu_id"}, exclude_none=True)
    for key, value in data.items():
        setattr(menu, key, value)
    menu.update_by = current.user.user_name
    menu.update_time = _now()
    db.add(menu)
    await db.commit()
    await db.refresh(menu)
    return Result.ok(data=dump_camel(_to_out(menu)), msg="修改成功")


async def delete_menus(db: AsyncSession, menu_ids: str, current: CurrentUserOut) -> Result:
    ids = parse_ids(menu_ids)
    if not ids:
        raise BizException(message=ResponseMsg.PARAM_ERROR, code=ResponseCode.PARAM_ERROR)
    for menu_id in ids:
        child = (await db.exec(select(SysMenu).where(SysMenu.parent_id == menu_id))).first()
        if child:
            raise BizException(message="存在子菜单，不允许删除", code=ResponseCode.PARAM_ERROR)
        menu = await db.get(SysMenu, menu_id)
        if menu is None:
            continue
        await db.delete(menu)
    await db.commit()
    return Result.ok(msg="删除成功")
