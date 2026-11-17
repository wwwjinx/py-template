from typing import Annotated

from fastapi import Depends, FastAPI

from app import config
from app.storage.base import FileStorage, StoredFile
from app.storage.local import LocalFileStorage, mount_local_uploads


def get_storage() -> FileStorage:
    """按配置返回存储实现。后续接 OSS/S3 时在这里加分支即可。"""
    backend = config.STORAGE_BACKEND
    if backend == "local":
        return LocalFileStorage(
            root=config.STORAGE_LOCAL_DIR,
            url_prefix=config.STORAGE_URL_PREFIX,
            public_base_url=config.STORAGE_PUBLIC_BASE_URL,
        )
    raise RuntimeError(f"unsupported storage backend: {backend}")


def mount_storage(application: FastAPI) -> None:
    if config.STORAGE_BACKEND == "local":
        mount_local_uploads(application, config.STORAGE_LOCAL_DIR, config.STORAGE_URL_PREFIX)


FileStorageDep = Annotated[FileStorage, Depends(get_storage)]

__all__ = [
    "FileStorage",
    "FileStorageDep",
    "StoredFile",
    "get_storage",
    "mount_storage",
]
