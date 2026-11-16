from typing import Any

from app.schemas.common import CamelModel, PageQuery


class OperLogQuery(PageQuery):
    title: str | None = None
    oper_name: str | None = None
    business_type: int | None = None
    status: int | None = None


class OperLogOut(CamelModel):
    oper_id: int
    title: str | None = None
    business_type: int | None = None
    method: str | None = None
    request_method: str | None = None
    operator_type: int | None = None
    oper_name: str | None = None
    dept_name: str | None = None
    oper_url: str | None = None
    oper_ip: str | None = None
    oper_location: str | None = None
    oper_param: str | None = None
    json_result: str | None = None
    status: int | None = None
    error_msg: str | None = None
    oper_time: Any = None
    cost_time: int | None = None


class LoginLogQuery(PageQuery):
    user_name: str | None = None
    ipaddr: str | None = None
    status: str | None = None


class LoginLogOut(CamelModel):
    info_id: int
    user_name: str | None = None
    ipaddr: str | None = None
    login_location: str | None = None
    browser: str | None = None
    os: str | None = None
    status: str | None = None
    msg: str | None = None
    login_time: Any = None
