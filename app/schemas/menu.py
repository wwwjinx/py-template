from typing import Any

from app.schemas.common import CamelModel


class MenuQuery(CamelModel):
    menu_name: str | None = None
    status: str | None = None
    visible: str | None = None


class MenuCreate(CamelModel):
    menu_name: str
    parent_id: int = 0
    order_num: int = 0
    path: str | None = ""
    component: str | None = None
    query: str | None = None
    route_name: str | None = ""
    is_frame: int | None = 1
    is_cache: int | None = 0
    menu_type: str
    visible: str | None = "0"
    status: str | None = "0"
    perms: str | None = None
    icon: str | None = "#"
    remark: str | None = ""


class MenuUpdate(MenuCreate):
    menu_id: int


class MenuOut(CamelModel):
    menu_id: int
    menu_name: str
    parent_id: int | None = 0
    order_num: int | None = 0
    path: str | None = None
    component: str | None = None
    query: str | None = None
    route_name: str | None = None
    is_frame: int | None = None
    is_cache: int | None = None
    menu_type: str | None = None
    visible: str | None = None
    status: str | None = None
    perms: str | None = None
    icon: str | None = None
    create_time: Any = None
    remark: str | None = None
    children: list[MenuOut] | None = None
