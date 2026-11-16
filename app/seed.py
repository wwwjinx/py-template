"""手动调用的种子数据：超管、部门、角色、菜单、字典。启动不会自动执行。"""

from datetime import UTC, datetime

from sqlalchemy import text
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.constants import ADMIN_ROLE_ID, ADMIN_USER_ID
from app.db import get_session_factory
from app.models.system import (
    SysDept,
    SysDictData,
    SysDictType,
    SysMenu,
    SysRole,
    SysRoleMenu,
    SysUser,
    SysUserRole,
)
from app.utils.password import hash_password

_NOW = None


def _now() -> datetime:
    return datetime.now(UTC)


# 部门：若依结构的总部及研发部门（admin 归属研发部）
_DEPTS = [
    SysDept(
        dept_id=100,
        parent_id=0,
        ancestors="0",
        dept_name="集团总公司",
        order_num=0,
        leader="admin",
        status="0",
        del_flag="0",
        create_by="admin",
    ),
    SysDept(
        dept_id=101,
        parent_id=100,
        ancestors="0,100",
        dept_name="深圳分公司",
        order_num=1,
        leader="admin",
        status="0",
        del_flag="0",
        create_by="admin",
    ),
    SysDept(
        dept_id=103,
        parent_id=101,
        ancestors="0,100,101",
        dept_name="研发部门",
        order_num=1,
        leader="admin",
        status="0",
        del_flag="0",
        create_by="admin",
    ),
]


def _menu(
    menu_id: int,
    name: str,
    parent_id: int,
    order_num: int,
    path: str,
    component: str | None,
    menu_type: str,
    perms: str,
    icon: str,
    *,
    remark: str = "",
) -> SysMenu:
    return SysMenu(
        menu_id=menu_id,
        menu_name=name,
        parent_id=parent_id,
        order_num=order_num,
        path=path,
        component=component,
        query="",
        route_name="",
        is_frame=1,
        is_cache=0,
        menu_type=menu_type,
        visible="0",
        status="0",
        perms=perms or None,
        icon=icon,
        create_by="admin",
        remark=remark,
    )


# path/component 对齐若依 Vue3 常规
_MENUS = [
    _menu(1, "系统管理", 0, 1, "system", None, "M", "", "system", remark="系统管理目录"),
    _menu(100, "用户管理", 1, 1, "user", "system/user/index", "C", "system:user:list", "user"),
    _menu(101, "角色管理", 1, 2, "role", "system/role/index", "C", "system:role:list", "peoples"),
    _menu(
        102, "菜单管理", 1, 3, "menu", "system/menu/index", "C", "system:menu:list", "tree-table"
    ),
    _menu(103, "部门管理", 1, 4, "dept", "system/dept/index", "C", "system:dept:list", "tree"),
    _menu(105, "字典管理", 1, 6, "dict", "system/dict/index", "C", "system:dict:list", "dict"),
    _menu(108, "日志管理", 1, 9, "log", "", "M", "", "log"),
    _menu(
        500,
        "操作日志",
        108,
        1,
        "operlog",
        "monitor/operlog/index",
        "C",
        "monitor:operlog:list",
        "form",
    ),
    _menu(
        501,
        "登录日志",
        108,
        2,
        "logininfor",
        "monitor/logininfor/index",
        "C",
        "monitor:logininfor:list",
        "logininfor",
    ),
    _menu(1000, "用户查询", 100, 1, "", "", "F", "system:user:query", "#"),
    _menu(1001, "用户新增", 100, 2, "", "", "F", "system:user:add", "#"),
    _menu(1002, "用户修改", 100, 3, "", "", "F", "system:user:edit", "#"),
    _menu(1003, "用户删除", 100, 4, "", "", "F", "system:user:remove", "#"),
    _menu(1006, "重置密码", 100, 7, "", "", "F", "system:user:resetPwd", "#"),
    _menu(1007, "角色查询", 101, 1, "", "", "F", "system:role:query", "#"),
    _menu(1008, "角色新增", 101, 2, "", "", "F", "system:role:add", "#"),
    _menu(1009, "角色修改", 101, 3, "", "", "F", "system:role:edit", "#"),
    _menu(1010, "角色删除", 101, 4, "", "", "F", "system:role:remove", "#"),
    _menu(1012, "菜单查询", 102, 1, "", "", "F", "system:menu:query", "#"),
    _menu(1013, "菜单新增", 102, 2, "", "", "F", "system:menu:add", "#"),
    _menu(1014, "菜单修改", 102, 3, "", "", "F", "system:menu:edit", "#"),
    _menu(1015, "菜单删除", 102, 4, "", "", "F", "system:menu:remove", "#"),
    _menu(1016, "部门查询", 103, 1, "", "", "F", "system:dept:query", "#"),
    _menu(1017, "部门新增", 103, 2, "", "", "F", "system:dept:add", "#"),
    _menu(1018, "部门修改", 103, 3, "", "", "F", "system:dept:edit", "#"),
    _menu(1019, "部门删除", 103, 4, "", "", "F", "system:dept:remove", "#"),
    _menu(1025, "字典查询", 105, 1, "#", "", "F", "system:dict:query", "#"),
    _menu(1026, "字典新增", 105, 2, "#", "", "F", "system:dict:add", "#"),
    _menu(1027, "字典修改", 105, 3, "#", "", "F", "system:dict:edit", "#"),
    _menu(1028, "字典删除", 105, 4, "#", "", "F", "system:dict:remove", "#"),
    _menu(1039, "操作查询", 500, 1, "#", "", "F", "monitor:operlog:query", "#"),
    _menu(1040, "操作删除", 500, 2, "#", "", "F", "monitor:operlog:remove", "#"),
    _menu(1042, "登录查询", 501, 1, "#", "", "F", "monitor:logininfor:query", "#"),
    _menu(1043, "登录删除", 501, 2, "#", "", "F", "monitor:logininfor:remove", "#"),
]


_DICT_TYPES = [
    (1, "用户性别", "sys_user_sex", "用户性别列表"),
    (2, "菜单状态", "sys_show_hide", "菜单状态列表"),
    (3, "系统开关", "sys_normal_disable", "系统开关列表"),
    (7, "系统是否", "sys_yes_no", "系统是否列表"),
    (10, "操作类型", "sys_oper_type", "操作类型列表"),
    (11, "系统状态", "sys_common_status", "登录状态列表"),
]

# (dict_code, sort, label, value, type, list_class, is_default, remark)
_DICT_DATA = [
    (1, 1, "男", "0", "sys_user_sex", "default", "Y", "性别男"),
    (2, 2, "女", "1", "sys_user_sex", "default", "N", "性别女"),
    (3, 3, "未知", "2", "sys_user_sex", "default", "N", "性别未知"),
    (4, 1, "显示", "0", "sys_show_hide", "primary", "Y", "显示菜单"),
    (5, 2, "隐藏", "1", "sys_show_hide", "danger", "N", "隐藏菜单"),
    (6, 1, "正常", "0", "sys_normal_disable", "primary", "Y", "正常状态"),
    (7, 2, "停用", "1", "sys_normal_disable", "danger", "N", "停用状态"),
    (15, 1, "是", "Y", "sys_yes_no", "primary", "Y", "系统默认是"),
    (16, 2, "否", "N", "sys_yes_no", "danger", "N", "系统默认否"),
    (21, 99, "其他", "0", "sys_oper_type", "info", "N", "其他操作"),
    (22, 1, "新增", "1", "sys_oper_type", "info", "N", "新增操作"),
    (23, 2, "修改", "2", "sys_oper_type", "info", "N", "修改操作"),
    (24, 3, "删除", "3", "sys_oper_type", "danger", "N", "删除操作"),
    (25, 4, "授权", "4", "sys_oper_type", "primary", "N", "授权操作"),
    (26, 5, "导出", "5", "sys_oper_type", "warning", "N", "导出操作"),
    (27, 6, "导入", "6", "sys_oper_type", "warning", "N", "导入操作"),
    (28, 7, "强退", "7", "sys_oper_type", "danger", "N", "强退操作"),
    (29, 8, "生成代码", "8", "sys_oper_type", "warning", "N", "生成操作"),
    (30, 9, "清空数据", "9", "sys_oper_type", "danger", "N", "清空操作"),
    (31, 1, "成功", "0", "sys_common_status", "primary", "N", "正常状态"),
    (32, 2, "失败", "1", "sys_common_status", "danger", "N", "停用状态"),
]


async def _reset_sequences(db: AsyncSession) -> None:
    """显式插入主键后，把 Postgres 序列调到当前最大值，避免后续新增冲突。"""
    bind = db.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    if dialect != "postgresql":
        return
    pairs = [
        ("sys_dept", "dept_id"),
        ("sys_user", "user_id"),
        ("sys_role", "role_id"),
        ("sys_menu", "menu_id"),
        ("sys_dict_type", "dict_id"),
        ("sys_dict_data", "dict_code"),
    ]
    for table, column in pairs:
        await db.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{table}', '{column}'), "
                f"COALESCE((SELECT MAX({column}) FROM {table}), 1))"
            )
        )


async def _seed(db: AsyncSession) -> str:
    exists = (await db.exec(select(SysUser).where(SysUser.user_name == "admin"))).first()
    if exists:
        return "skipped: admin already exists"

    now = _now()
    for dept in _DEPTS:
        dept.create_time = now
        db.add(dept)

    db.add(
        SysRole(
            role_id=ADMIN_ROLE_ID,
            role_name="超级管理员",
            role_key="admin",
            role_sort=1,
            data_scope="1",
            menu_check_strictly=1,
            dept_check_strictly=1,
            status="0",
            del_flag="0",
            create_by="admin",
            create_time=now,
            remark="超级管理员",
        )
    )

    for menu in _MENUS:
        menu.create_time = now
        db.add(menu)

    db.add(
        SysUser(
            user_id=ADMIN_USER_ID,
            dept_id=103,
            user_name="admin",
            nick_name="超级管理员",
            user_type="00",
            email="",
            phonenumber="",
            sex="0",
            avatar="",
            time_zone="auto",
            password=hash_password("admin123"),
            status="0",
            del_flag="0",
            create_by="admin",
            create_time=now,
            pwd_update_date=now,
            remark="管理员",
        )
    )
    db.add(SysUserRole(user_id=ADMIN_USER_ID, role_id=ADMIN_ROLE_ID))
    for menu in _MENUS:
        db.add(SysRoleMenu(role_id=ADMIN_ROLE_ID, menu_id=menu.menu_id))

    for dict_id, name, dict_type, remark in _DICT_TYPES:
        db.add(
            SysDictType(
                dict_id=dict_id,
                dict_name=name,
                dict_type=dict_type,
                status="0",
                create_by="admin",
                create_time=now,
                remark=remark,
            )
        )
    for code, sort, label, value, typ, list_class, is_default, remark in _DICT_DATA:
        db.add(
            SysDictData(
                dict_code=code,
                dict_sort=sort,
                dict_label=label,
                dict_value=value,
                dict_type=typ,
                list_class=list_class,
                is_default=is_default,
                status="0",
                create_by="admin",
                create_time=now,
                remark=remark,
            )
        )

    await db.commit()
    await _reset_sequences(db)
    await db.commit()
    return "seeded admin / admin123"


async def seed_admin() -> str:
    """写入超管与基础菜单/字典。若已有 admin 用户则跳过，可重复调用。"""
    async with get_session_factory()() as db:
        return await _seed(db)


if __name__ == "__main__":
    import asyncio

    from app.db import init_db

    async def _main() -> None:
        await init_db()
        print(await seed_admin())

    asyncio.run(_main())
