from typing import Any

from app.schemas.common import CamelModel, PageQuery


class DictTypeQuery(PageQuery):
    dict_name: str | None = None
    dict_type: str | None = None
    status: str | None = None


class DictTypeCreate(CamelModel):
    dict_name: str
    dict_type: str
    status: str | None = "0"
    remark: str | None = None


class DictTypeUpdate(DictTypeCreate):
    dict_id: int


class DictTypeOut(CamelModel):
    dict_id: int
    dict_name: str | None = None
    dict_type: str | None = None
    status: str | None = None
    create_by: str | None = None
    create_time: Any = None
    remark: str | None = None


class DictDataQuery(PageQuery):
    dict_type: str | None = None
    dict_label: str | None = None
    status: str | None = None


class DictDataCreate(CamelModel):
    dict_sort: int | None = 0
    dict_label: str
    dict_value: str
    dict_type: str
    css_class: str | None = None
    list_class: str | None = None
    is_default: str | None = "N"
    status: str | None = "0"
    remark: str | None = None


class DictDataUpdate(DictDataCreate):
    dict_code: int


class DictDataOut(CamelModel):
    dict_code: int
    dict_sort: int | None = 0
    dict_label: str | None = None
    dict_value: str | None = None
    dict_type: str | None = None
    css_class: str | None = None
    list_class: str | None = None
    is_default: str | None = None
    status: str | None = None
    create_time: Any = None
    remark: str | None = None
