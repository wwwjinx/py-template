from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class StoredFile:
    """一次保存的结果。key 是存储内路径，url 是给前端访问的地址。"""

    key: str
    filename: str
    content_type: str | None
    size: int
    url: str


@runtime_checkable
class FileStorage(Protocol):
    """统一文件存储接口。本地磁盘先实现，云厂商 OSS/S3 只要再写一个同类即可。"""

    async def save(
        self,
        data: bytes,
        *,
        filename: str,
        content_type: str | None = None,
    ) -> StoredFile:
        """保存文件，返回 key 与可访问 url。"""
        ...

    async def read(self, key: str) -> bytes:
        """按 key 读取文件内容。不存在时抛 FileNotFoundError。"""
        ...

    async def delete(self, key: str) -> None:
        """按 key 删除。不存在时抛 FileNotFoundError。"""
        ...

    def url_for(self, key: str) -> str:
        """由 key 生成访问 url，不检查文件是否存在。"""
        ...
