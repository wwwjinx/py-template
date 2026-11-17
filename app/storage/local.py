from __future__ import annotations

import asyncio
import uuid
from datetime import date
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.storage.base import StoredFile


class LocalFileStorage:
    """把文件写到本地目录。key 形如 2026/11/17/<uuid>.png。"""

    def __init__(
        self,
        root: str | Path,
        *,
        url_prefix: str = "/uploads",
        public_base_url: str = "",
    ) -> None:
        self.root = Path(root)
        self.url_prefix = "/" + url_prefix.strip("/")
        self.public_base_url = public_base_url.rstrip("/")

    def _resolve(self, key: str) -> Path:
        rel = Path(key.replace("\\", "/"))
        if rel.is_absolute() or ".." in rel.parts or not key.strip():
            raise ValueError("invalid storage key")
        path = (self.root / rel).resolve()
        root = self.root.resolve()
        if path != root and root not in path.parents:
            raise ValueError("invalid storage key")
        return path

    def url_for(self, key: str) -> str:
        rel = key.lstrip("/")
        path = f"{self.url_prefix}/{rel}"
        if self.public_base_url:
            return f"{self.public_base_url}{path}"
        return path

    async def save(
        self,
        data: bytes,
        *,
        filename: str,
        content_type: str | None = None,
    ) -> StoredFile:
        suffix = Path(filename).suffix.lower()
        today = date.today()
        key = f"{today:%Y/%m/%d}/{uuid.uuid4().hex}{suffix}"
        dest = self._resolve(key)
        await asyncio.to_thread(self._write, dest, data)
        return StoredFile(
            key=key,
            filename=Path(filename).name,
            content_type=content_type,
            size=len(data),
            url=self.url_for(key),
        )

    async def read(self, key: str) -> bytes:
        path = self._resolve(key)
        return await asyncio.to_thread(self._read, path)

    async def delete(self, key: str) -> None:
        path = self._resolve(key)
        await asyncio.to_thread(self._delete, path)

    @staticmethod
    def _write(path: Path, data: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    @staticmethod
    def _read(path: Path) -> bytes:
        if not path.is_file():
            raise FileNotFoundError(path)
        return path.read_bytes()

    @staticmethod
    def _delete(path: Path) -> None:
        if not path.is_file():
            raise FileNotFoundError(path)
        path.unlink()


def mount_local_uploads(application: FastAPI, root: str | Path, url_prefix: str) -> None:
    directory = Path(root)
    directory.mkdir(parents=True, exist_ok=True)
    application.mount(url_prefix.rstrip("/") or "/uploads", StaticFiles(directory=directory), name="uploads")
