"""登录、当前用户与侧边栏路由。"""

from datetime import UTC, datetime

from fastapi import Request
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.constants import (
    ADMIN_USER_ID,
    ALL_PERMISSION,
    DEL_FLAG_NORMAL,
    INNER_LINK,
    LAYOUT,
    LOGIN_FAIL,
    LOGIN_SUCCESS,
    MENU_ROOT_ID,
    MENU_TYPE_DIR,
    MENU_TYPE_MENU,
    NO_FRAME,
    PARENT_VIEW,
    STATUS_NORMAL,
)
from app.core.exceptions import BizException
from app.enums import ResponseCode
from app.models.system import (
    SysDept,
    SysLogininfor,
    SysMenu,
    SysRole,
    SysRoleMenu,
    SysUser,
    SysUserRole,
)
from app.schemas.common import dump_camel
from app.schemas.login import CurrentUserOut, MetaModel, RouterModel, UserInfoOut
from app.utils.jwt import create_access_token
from app.utils.password import verify_password
from app.utils.result import Result


def _client_ip(request: Request | None) -> str:
    if request is None:
        return ""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""


async def add_login_log(
    db: AsyncSession,
    *,
    user_name: str,
    status: str,
    msg: str,
    request: Request | None = None,
) -> None:
    row = SysLogininfor(
        user_name=user_name,
        ipaddr=_client_ip(request),
        login_location="",
        browser="",
        os="",
        status=status,
        msg=msg,
        login_time=datetime.now(UTC),
    )
    db.add(row)
    await db.commit()


async def _find_user_by_name(db: AsyncSession, username: str) -> SysUser | None:
    result = await db.exec(
        select(SysUser).where(SysUser.user_name == username, SysUser.del_flag == DEL_FLAG_NORMAL)
    )
    return result.first()


async def login(
    db: AsyncSession, username: str, password: str, request: Request | None = None
) -> Result:
    user = await _find_user_by_name(db, username)
    if user is None or not verify_password(password, user.password):
        await add_login_log(
            db, user_name=username, status=LOGIN_FAIL, msg="用户不存在或密码错误", request=request
        )
        raise BizException(message="用户不存在或密码错误", code=ResponseCode.UNAUTHORIZED)
    if user.status != STATUS_NORMAL:
        await add_login_log(
            db, user_name=username, status=LOGIN_FAIL, msg="用户已停用", request=request
        )
        raise BizException(message="用户已停用", code=ResponseCode.UNAUTHORIZED)

    user.login_ip = _client_ip(request)
    user.login_date = datetime.now(UTC)
    db.add(user)
    await db.commit()
    await add_login_log(
        db, user_name=username, status=LOGIN_SUCCESS, msg="登录成功", request=request
    )

    token = create_access_token({"user_id": user.user_id, "user_name": user.user_name})
    return Result.ok(data={"token": token}, msg="登录成功")


async def logout(
    db: AsyncSession, current: CurrentUserOut, request: Request | None = None
) -> Result:
    await add_login_log(
        db,
        user_name=current.user.user_name,
        status=LOGIN_SUCCESS,
        msg="退出成功",
        request=request,
    )
    return Result.ok(msg="退出成功")


async def _user_roles(db: AsyncSession, user_id: int) -> list[SysRole]:
    result = await db.exec(
        select(SysRole)
        .join(SysUserRole, col(SysUserRole.role_id) == col(SysRole.role_id))
        .where(
            SysUserRole.user_id == user_id,
            SysRole.del_flag == DEL_FLAG_NORMAL,
            SysRole.status == STATUS_NORMAL,
        )
    )
    return list(result.all())


async def _menus_for_user(db: AsyncSession, user_id: int) -> list[SysMenu]:
    if user_id == ADMIN_USER_ID:
        result = await db.exec(
            select(SysMenu)
            .where(SysMenu.status == STATUS_NORMAL)
            .order_by(col(SysMenu.parent_id), col(SysMenu.order_num))
        )
        return list(result.all())
    result = await db.exec(
        select(SysMenu)
        .join(SysRoleMenu, col(SysRoleMenu.menu_id) == col(SysMenu.menu_id))
        .join(SysUserRole, col(SysUserRole.role_id) == col(SysRoleMenu.role_id))
        .join(SysRole, col(SysRole.role_id) == col(SysUserRole.role_id))
        .where(
            SysUserRole.user_id == user_id,
            SysMenu.status == STATUS_NORMAL,
            SysRole.del_flag == DEL_FLAG_NORMAL,
            SysRole.status == STATUS_NORMAL,
        )
        .distinct()
        .order_by(col(SysMenu.parent_id), col(SysMenu.order_num))
    )
    return list(result.all())


async def load_current_user(db: AsyncSession, user_id: int) -> CurrentUserOut:
    user = await db.get(SysUser, user_id)
    if user is None or user.del_flag != DEL_FLAG_NORMAL:
        raise BizException(message="用户不存在或已被删除", code=ResponseCode.UNAUTHORIZED)
    if user.status != STATUS_NORMAL:
        raise BizException(message="用户已停用", code=ResponseCode.UNAUTHORIZED)

    roles = await _user_roles(db, user_id)
    menus = await _menus_for_user(db, user_id)
    is_admin = user_id == ADMIN_USER_ID
    permissions = [ALL_PERMISSION] if is_admin else [m.perms for m in menus if m.perms]
    role_keys = [r.role_key for r in roles]
    if is_admin and "admin" not in role_keys:
        role_keys = ["admin", *role_keys]

    dept = None
    if user.dept_id:
        dept_row = await db.get(SysDept, user.dept_id)
        if dept_row and dept_row.del_flag == DEL_FLAG_NORMAL:
            dept = {
                "deptId": dept_row.dept_id,
                "deptName": dept_row.dept_name,
                "status": dept_row.status,
            }

    info = UserInfoOut.model_validate(user)
    info.admin = is_admin
    info.dept = dept
    info.roles = [
        {"roleId": r.role_id, "roleName": r.role_name, "roleKey": r.role_key, "status": r.status}
        for r in roles
    ]
    return CurrentUserOut(permissions=permissions, roles=role_keys, user=info)


async def get_info(db: AsyncSession, current: CurrentUserOut) -> Result:
    # 重新查一遍，保证角色/权限是最新的
    fresh = await load_current_user(db, current.user.user_id)
    return Result.ok(data=dump_camel(fresh))


def _is_http(link: str | None) -> bool:
    return bool(link) and link.startswith(("http://", "https://"))


def _is_menu_frame(menu: SysMenu) -> bool:
    return (
        menu.parent_id == MENU_ROOT_ID
        and menu.menu_type == MENU_TYPE_MENU
        and menu.is_frame == NO_FRAME
    )


def _is_inner_link(menu: SysMenu) -> bool:
    return menu.is_frame == NO_FRAME and _is_http(menu.path)


def _is_parent_view(menu: SysMenu) -> bool:
    return menu.parent_id != MENU_ROOT_ID and menu.menu_type == MENU_TYPE_DIR


def _route_name(name: str | None, path: str | None) -> str:
    router_name = name if name else (path or "")
    return router_name.capitalize()


def _router_name(menu: SysMenu) -> str:
    if _is_menu_frame(menu):
        return ""
    return _route_name(menu.route_name, menu.path)


def _inner_link_replace(path: str) -> str:
    for old, new in (("http://", ""), ("https://", ""), ("www.", ""), (".", "/"), (":", "/")):
        path = path.replace(old, new)
    return path


def _router_path(menu: SysMenu) -> str | None:
    router_path = menu.path
    if menu.parent_id != MENU_ROOT_ID and _is_inner_link(menu) and router_path:
        router_path = _inner_link_replace(router_path)
    if (
        menu.parent_id == MENU_ROOT_ID
        and menu.menu_type == MENU_TYPE_DIR
        and menu.is_frame == NO_FRAME
    ):
        router_path = f"/{menu.path}"
    elif _is_menu_frame(menu):
        router_path = "/"
    return router_path


def _component(menu: SysMenu) -> str:
    component = LAYOUT
    if menu.component and not _is_menu_frame(menu):
        component = menu.component
    elif not menu.component and menu.parent_id != MENU_ROOT_ID and _is_inner_link(menu):
        component = INNER_LINK
    elif not menu.component and _is_parent_view(menu):
        component = PARENT_VIEW
    return component


def _build_menu_tree(pid: int, menus: list[SysMenu]) -> list[SysMenu]:
    # 只按 parent 分组，真正树在 router 生成时展开
    return [m for m in menus if (m.parent_id or 0) == pid]


def _generate_routers(pid: int, menus: list[SysMenu]) -> list[RouterModel]:
    routers: list[RouterModel] = []
    for menu in _build_menu_tree(pid, menus):
        children_menus = _build_menu_tree(menu.menu_id or 0, menus)
        router = RouterModel(
            hidden=menu.visible == "1",
            name=_router_name(menu),
            path=_router_path(menu),
            component=_component(menu),
            query=menu.query,
            meta=MetaModel(
                title=menu.menu_name,
                icon=menu.icon,
                no_cache=menu.is_cache == 1,
                link=menu.path if _is_http(menu.path) else None,
            ),
        )
        if children_menus and menu.menu_type == MENU_TYPE_DIR:
            router.always_show = True
            router.redirect = "noRedirect"
            router.children = _generate_routers(menu.menu_id or 0, menus)
        elif _is_menu_frame(menu):
            router.meta = None
            router.children = [
                RouterModel(
                    path=menu.path,
                    component=menu.component,
                    name=_route_name(menu.route_name, menu.path),
                    meta=MetaModel(
                        title=menu.menu_name,
                        icon=menu.icon,
                        no_cache=menu.is_cache == 1,
                        link=menu.path if _is_http(menu.path) else None,
                    ),
                    query=menu.query,
                )
            ]
        elif menu.parent_id == MENU_ROOT_ID and _is_inner_link(menu):
            router.meta = MetaModel(title=menu.menu_name, icon=menu.icon)
            router.path = "/"
            router_path = _inner_link_replace(menu.path or "")
            router.children = [
                RouterModel(
                    path=router_path,
                    component=INNER_LINK,
                    name=_route_name(menu.route_name, menu.path),
                    meta=MetaModel(
                        title=menu.menu_name,
                        icon=menu.icon,
                        link=menu.path if _is_http(menu.path) else None,
                    ),
                )
            ]
        routers.append(router)
    return routers


async def get_routers(db: AsyncSession, current: CurrentUserOut) -> Result:
    menus = await _menus_for_user(db, current.user.user_id)
    sidebar = [m for m in menus if m.menu_type in (MENU_TYPE_DIR, MENU_TYPE_MENU)]
    sidebar.sort(key=lambda m: (m.parent_id or 0, m.order_num or 0))
    routers = _generate_routers(MENU_ROOT_ID, sidebar)
    return Result.ok(data=[r.model_dump(by_alias=True, exclude_none=True) for r in routers])
