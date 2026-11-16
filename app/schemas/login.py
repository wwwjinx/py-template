from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.schemas.common import CamelModel


class LoginBody(BaseModel):
    """登录入参：优先 username，同时兼容若依的 userName。"""

    model_config = ConfigDict(populate_by_name=True)

    username: str = Field(validation_alias=AliasChoices("username", "userName", "user_name"))
    password: str


class UserInfoOut(CamelModel):
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
    remark: str | None = None
    admin: bool = False
    dept: dict[str, Any] | None = None
    roles: list[dict[str, Any]] = Field(default_factory=list)


class MetaModel(CamelModel):
    title: str | None = None
    icon: str | None = None
    no_cache: bool | None = None
    link: str | None = None


class RouterModel(CamelModel):
    name: str | None = None
    path: str | None = None
    hidden: bool | None = None
    redirect: str | None = None
    component: str | None = None
    query: str | None = None
    always_show: bool | None = None
    meta: MetaModel | None = None
    children: list[RouterModel] | None = None


class CurrentUserOut(CamelModel):
    permissions: list[str]
    roles: list[str]
    user: UserInfoOut
