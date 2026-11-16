from typing import Any

from app.schemas.common import CamelModel, PageQuery


class UserQuery(PageQuery):
    user_name: str | None = None
    phonenumber: str | None = None
    status: str | None = None
    dept_id: int | None = None


class UserCreate(CamelModel):
    user_name: str
    nick_name: str
    password: str
    dept_id: int | None = None
    email: str | None = None
    phonenumber: str | None = None
    sex: str | None = "0"
    status: str | None = "0"
    remark: str | None = None
    role_ids: list[int] | None = None


class UserUpdate(CamelModel):
    user_id: int
    nick_name: str | None = None
    dept_id: int | None = None
    email: str | None = None
    phonenumber: str | None = None
    sex: str | None = None
    status: str | None = None
    remark: str | None = None
    role_ids: list[int] | None = None


class UserStatusBody(CamelModel):
    user_id: int
    status: str


class ResetPwdBody(CamelModel):
    user_id: int
    password: str


class UserOut(CamelModel):
    user_id: int
    dept_id: int | None = None
    user_name: str
    nick_name: str
    user_type: str | None = None
    email: str | None = None
    phonenumber: str | None = None
    sex: str | None = None
    avatar: str | None = None
    status: str | None = None
    del_flag: str | None = None
    login_ip: str | None = None
    login_date: Any = None
    create_by: str | None = None
    create_time: Any = None
    remark: str | None = None
    admin: bool = False
    dept: dict[str, Any] | None = None
    role_ids: list[int] | None = None
    roles: list[dict[str, Any]] | None = None
