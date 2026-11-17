from pathlib import Path

from fastapi import UploadFile

from app import config
from app.core.exceptions import BizException
from app.enums import ResponseCode, ResponseMsg
from app.schemas.file import UploadedFileOut
from app.storage.base import FileStorage
from app.utils.result import Result

_CHUNK = 64 * 1024


def _extension(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")


async def _read_limited(file: UploadFile, max_bytes: int) -> bytes:
    buf = bytearray()
    while True:
        chunk = await file.read(_CHUNK)
        if not chunk:
            break
        buf.extend(chunk)
        if len(buf) > max_bytes:
            raise BizException(message="文件过大", code=ResponseCode.PARAM_ERROR)
    return bytes(buf)


async def save_upload(storage: FileStorage, file: UploadFile) -> UploadedFileOut:
    filename = Path(file.filename or "").name
    if not filename or filename in {".", ".."}:
        raise BizException(message="请选择文件", code=ResponseCode.PARAM_ERROR)
    ext = _extension(filename)
    if not ext or ext not in config.STORAGE_ALLOWED_EXTS:
        raise BizException(message="不支持的文件类型", code=ResponseCode.PARAM_ERROR)

    max_bytes = config.STORAGE_MAX_SIZE_MB * 1024 * 1024
    data = await _read_limited(file, max_bytes)
    if not data:
        raise BizException(message="请选择文件", code=ResponseCode.PARAM_ERROR)

    stored = await storage.save(data, filename=filename, content_type=file.content_type)
    return UploadedFileOut(
        url=stored.url,
        fileName=stored.key,
        newFileName=Path(stored.key).name,
        originalFilename=stored.filename,
        size=stored.size,
    )


async def upload(storage: FileStorage, file: UploadFile) -> Result[UploadedFileOut]:
    return Result.ok(data=await save_upload(storage, file), msg="上传成功")


async def upload_many(storage: FileStorage, files: list[UploadFile]) -> Result[list[UploadedFileOut]]:
    if not files:
        raise BizException(message="请选择文件", code=ResponseCode.PARAM_ERROR)
    items = [await save_upload(storage, item) for item in files]
    return Result.ok(data=items, msg="上传成功")


async def download(storage: FileStorage, key: str) -> tuple[bytes, str]:
    if not key or not key.strip():
        raise BizException(message=ResponseMsg.PARAM_ERROR, code=ResponseCode.PARAM_ERROR)
    try:
        data = await storage.read(key)
    except ValueError as exc:
        raise BizException(message=ResponseMsg.PARAM_ERROR, code=ResponseCode.PARAM_ERROR) from exc
    except FileNotFoundError as exc:
        raise BizException(message="文件不存在", code=ResponseCode.NOT_FOUND) from exc
    return data, Path(key).name
