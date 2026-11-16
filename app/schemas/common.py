from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """请求/响应模型：JSON 用 camelCase，也接受原字段名。"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class PageQuery(CamelModel):
    page_num: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=1000)


def dump_camel(obj: BaseModel | list[BaseModel] | None) -> Any:
    if obj is None:
        return None
    if isinstance(obj, list):
        return [item.model_dump(by_alias=True) for item in obj]
    return obj.model_dump(by_alias=True)


def page_data(rows: list[Any], total: int) -> dict[str, Any]:
    return {"rows": rows, "total": total}


def parse_ids(raw: str) -> list[int]:
    ids: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        ids.append(int(part))
    return ids
