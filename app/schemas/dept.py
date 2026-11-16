from typing import Any

from app.schemas.common import CamelModel


class DeptQuery(CamelModel):
    dept_name: str | None = None
    status: str | None = None


class DeptCreate(CamelModel):
    parent_id: int = 0
    dept_name: str
    order_num: int = 0
    leader: str | None = None
    phone: str | None = None
    email: str | None = None
    status: str | None = "0"


class DeptUpdate(DeptCreate):
    dept_id: int


class DeptOut(CamelModel):
    dept_id: int
    parent_id: int | None = 0
    ancestors: str | None = None
    dept_name: str | None = None
    order_num: int | None = 0
    leader: str | None = None
    phone: str | None = None
    email: str | None = None
    status: str | None = None
    create_time: Any = None
    children: list[DeptOut] | None = None
