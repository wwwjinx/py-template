from typing import Any

from app.schemas.common import CamelModel, PageQuery


class RoleQuery(PageQuery):
    role_name: str | None = None
    role_key: str | None = None
    status: str | None = None


class RoleCreate(CamelModel):
    role_name: str
    role_key: str
    role_sort: int
    status: str = "0"
    remark: str | None = None
    menu_ids: list[int] | None = None
    menu_check_strictly: int | None = 1
    dept_check_strictly: int | None = 1
    data_scope: str | None = "1"


class RoleUpdate(RoleCreate):
    role_id: int


class RoleStatusBody(CamelModel):
    role_id: int
    status: str


class RoleOut(CamelModel):
    role_id: int
    role_name: str
    role_key: str
    role_sort: int
    data_scope: str | None = None
    menu_check_strictly: int | None = None
    dept_check_strictly: int | None = None
    status: str
    del_flag: str | None = None
    create_by: str | None = None
    create_time: Any = None
    remark: str | None = None
    menu_ids: list[int] | None = None
    flag: bool | None = None
