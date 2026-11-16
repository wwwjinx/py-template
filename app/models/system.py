"""若依系统管理相关表的 SQLModel 映射，表名与字段与 ruoyi-fastapi-pg.sql 对齐。"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Identity,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlmodel import Field, SQLModel

# Postgres 用 bigserial；SQLite 只有 INTEGER PRIMARY KEY 才会自增。
_PK_INT = BigInteger().with_variant(Integer(), "sqlite")


def _bigint_pk() -> Column:
    return Column(_PK_INT, Identity(always=False), primary_key=True, autoincrement=True)


class SysDept(SQLModel, table=True):
    __tablename__ = "sys_dept"

    dept_id: int | None = Field(default=None, sa_column=_bigint_pk())
    parent_id: int | None = Field(default=0, sa_column=Column(BigInteger, default=0))
    ancestors: str | None = Field(default="", sa_column=Column(String(50), default=""))
    dept_name: str | None = Field(default="", sa_column=Column(String(30), default=""))
    order_num: int | None = Field(default=0, sa_column=Column(Integer, default=0))
    leader: str | None = Field(default=None, sa_column=Column(String(20), default=None))
    phone: str | None = Field(default=None, sa_column=Column(String(11), default=None))
    email: str | None = Field(default=None, sa_column=Column(String(50), default=None))
    status: str | None = Field(default="0", sa_column=Column(String(1), default="0"))
    del_flag: str | None = Field(default="0", sa_column=Column(String(1), default="0"))
    create_by: str | None = Field(default="", sa_column=Column(String(64), default=""))
    create_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    update_by: str | None = Field(default="", sa_column=Column(String(64), default=""))
    update_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))


class SysUser(SQLModel, table=True):
    __tablename__ = "sys_user"

    user_id: int | None = Field(default=None, sa_column=_bigint_pk())
    dept_id: int | None = Field(default=None, sa_column=Column(BigInteger, default=None))
    user_name: str = Field(sa_column=Column(String(30), nullable=False))
    nick_name: str = Field(sa_column=Column(String(30), nullable=False))
    user_type: str | None = Field(default="00", sa_column=Column(String(2), default="00"))
    email: str | None = Field(default="", sa_column=Column(String(50), default=""))
    phonenumber: str | None = Field(default="", sa_column=Column(String(11), default=""))
    sex: str | None = Field(default="0", sa_column=Column(String(1), default="0"))
    avatar: str | None = Field(default="", sa_column=Column(String(100), default=""))
    time_zone: str = Field(
        default="auto", sa_column=Column(String(64), nullable=False, default="auto")
    )
    password: str | None = Field(default="", sa_column=Column(String(100), default=""))
    status: str | None = Field(default="0", sa_column=Column(String(1), default="0"))
    del_flag: str | None = Field(default="0", sa_column=Column(String(1), default="0"))
    login_ip: str | None = Field(default="", sa_column=Column(String(128), default=""))
    login_date: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    pwd_update_date: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    create_by: str | None = Field(default="", sa_column=Column(String(64), default=""))
    create_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    update_by: str | None = Field(default="", sa_column=Column(String(64), default=""))
    update_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    remark: str | None = Field(default=None, sa_column=Column(String(500), default=None))


class SysRole(SQLModel, table=True):
    __tablename__ = "sys_role"

    role_id: int | None = Field(default=None, sa_column=_bigint_pk())
    role_name: str = Field(sa_column=Column(String(30), nullable=False))
    role_key: str = Field(sa_column=Column(String(100), nullable=False))
    role_sort: int = Field(sa_column=Column(Integer, nullable=False))
    data_scope: str | None = Field(default="1", sa_column=Column(String(1), default="1"))
    menu_check_strictly: int | None = Field(default=1, sa_column=Column(SmallInteger, default=1))
    dept_check_strictly: int | None = Field(default=1, sa_column=Column(SmallInteger, default=1))
    status: str = Field(sa_column=Column(String(1), nullable=False))
    del_flag: str | None = Field(default="0", sa_column=Column(String(1), default="0"))
    create_by: str | None = Field(default="", sa_column=Column(String(64), default=""))
    create_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    update_by: str | None = Field(default="", sa_column=Column(String(64), default=""))
    update_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    remark: str | None = Field(default=None, sa_column=Column(String(500), default=None))


class SysMenu(SQLModel, table=True):
    __tablename__ = "sys_menu"

    menu_id: int | None = Field(default=None, sa_column=_bigint_pk())
    menu_name: str = Field(sa_column=Column(String(50), nullable=False))
    parent_id: int | None = Field(default=0, sa_column=Column(BigInteger, default=0))
    order_num: int | None = Field(default=0, sa_column=Column(Integer, default=0))
    path: str | None = Field(default="", sa_column=Column(String(200), default=""))
    component: str | None = Field(default=None, sa_column=Column(String(255), default=None))
    query: str | None = Field(default=None, sa_column=Column(String(255), default=None))
    route_name: str | None = Field(default="", sa_column=Column(String(50), default=""))
    is_frame: int | None = Field(default=1, sa_column=Column(Integer, default=1))
    is_cache: int | None = Field(default=0, sa_column=Column(Integer, default=0))
    menu_type: str | None = Field(default="", sa_column=Column(String(1), default=""))
    visible: str | None = Field(default="0", sa_column=Column(String(1), default="0"))
    status: str | None = Field(default="0", sa_column=Column(String(1), default="0"))
    perms: str | None = Field(default=None, sa_column=Column(String(100), default=None))
    icon: str | None = Field(default="#", sa_column=Column(String(100), default="#"))
    create_by: str | None = Field(default="", sa_column=Column(String(64), default=""))
    create_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    update_by: str | None = Field(default="", sa_column=Column(String(64), default=""))
    update_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    remark: str | None = Field(default="", sa_column=Column(String(500), default=""))


class SysUserRole(SQLModel, table=True):
    __tablename__ = "sys_user_role"

    user_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    role_id: int = Field(sa_column=Column(BigInteger, primary_key=True))


class SysRoleMenu(SQLModel, table=True):
    __tablename__ = "sys_role_menu"

    role_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    menu_id: int = Field(sa_column=Column(BigInteger, primary_key=True))


class SysRoleDept(SQLModel, table=True):
    """数据权限部门关联。第一期建表占位，不做复杂过滤。"""

    __tablename__ = "sys_role_dept"

    role_id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    dept_id: int = Field(sa_column=Column(BigInteger, primary_key=True))


class SysDictType(SQLModel, table=True):
    __tablename__ = "sys_dict_type"
    __table_args__ = (UniqueConstraint("dict_type"),)

    dict_id: int | None = Field(default=None, sa_column=_bigint_pk())
    dict_name: str | None = Field(default="", sa_column=Column(String(100), default=""))
    dict_type: str | None = Field(default="", sa_column=Column(String(100), default=""))
    status: str | None = Field(default="0", sa_column=Column(String(1), default="0"))
    create_by: str | None = Field(default="", sa_column=Column(String(64), default=""))
    create_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    update_by: str | None = Field(default="", sa_column=Column(String(64), default=""))
    update_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    remark: str | None = Field(default=None, sa_column=Column(String(500), default=None))


class SysDictData(SQLModel, table=True):
    __tablename__ = "sys_dict_data"

    dict_code: int | None = Field(default=None, sa_column=_bigint_pk())
    dict_sort: int | None = Field(default=0, sa_column=Column(Integer, default=0))
    dict_label: str | None = Field(default="", sa_column=Column(String(100), default=""))
    dict_value: str | None = Field(default="", sa_column=Column(String(100), default=""))
    dict_type: str | None = Field(default="", sa_column=Column(String(100), default=""))
    css_class: str | None = Field(default=None, sa_column=Column(String(100), default=None))
    list_class: str | None = Field(default=None, sa_column=Column(String(100), default=None))
    is_default: str | None = Field(default="N", sa_column=Column(String(1), default="N"))
    status: str | None = Field(default="0", sa_column=Column(String(1), default="0"))
    create_by: str | None = Field(default="", sa_column=Column(String(64), default=""))
    create_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    update_by: str | None = Field(default="", sa_column=Column(String(64), default=""))
    update_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    remark: str | None = Field(default=None, sa_column=Column(String(500), default=None))


class SysOperLog(SQLModel, table=True):
    __tablename__ = "sys_oper_log"

    oper_id: int | None = Field(default=None, sa_column=_bigint_pk())
    title: str | None = Field(default="", sa_column=Column(String(50), default=""))
    business_type: int | None = Field(default=0, sa_column=Column(Integer, default=0))
    method: str | None = Field(default="", sa_column=Column(String(100), default=""))
    request_method: str | None = Field(default="", sa_column=Column(String(10), default=""))
    operator_type: int | None = Field(default=0, sa_column=Column(Integer, default=0))
    oper_name: str | None = Field(default="", sa_column=Column(String(50), default=""))
    dept_name: str | None = Field(default="", sa_column=Column(String(50), default=""))
    oper_url: str | None = Field(default="", sa_column=Column(String(255), default=""))
    oper_ip: str | None = Field(default="", sa_column=Column(String(128), default=""))
    oper_location: str | None = Field(default="", sa_column=Column(String(255), default=""))
    oper_param: str | None = Field(default="", sa_column=Column(String(2000), default=""))
    json_result: str | None = Field(default="", sa_column=Column(String(2000), default=""))
    status: int | None = Field(default=0, sa_column=Column(Integer, default=0))
    error_msg: str | None = Field(default="", sa_column=Column(String(2000), default=""))
    oper_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    cost_time: int | None = Field(default=0, sa_column=Column(BigInteger, default=0))


class SysLogininfor(SQLModel, table=True):
    __tablename__ = "sys_logininfor"

    info_id: int | None = Field(default=None, sa_column=_bigint_pk())
    user_name: str | None = Field(default="", sa_column=Column(String(50), default=""))
    ipaddr: str | None = Field(default="", sa_column=Column(String(128), default=""))
    login_location: str | None = Field(default="", sa_column=Column(String(255), default=""))
    browser: str | None = Field(default="", sa_column=Column(String(50), default=""))
    os: str | None = Field(default="", sa_column=Column(String(50), default=""))
    status: str | None = Field(default="0", sa_column=Column(String(1), default="0"))
    msg: str | None = Field(default="", sa_column=Column(String(255), default=""))
    login_time: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True)))
