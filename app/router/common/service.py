from datetime import UTC, datetime
from pathlib import Path

from fastapi import UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession

from app import config
from app.constants import DEL_FLAG_NORMAL
from app.core.exceptions import BizException
from app.enums import ResponseCode, ResponseMsg
from app.models.system import SysFile
from app.schemas.file import UploadedFileOut
from app.schemas.login import CurrentUserOut
from app.storage.base import FileStorage
from app.utils.result import Result

_CHUNK = 64 * 1024


def _now() -> datetime:
    return datetime.now(UTC)


def _extension(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")


def _to_out(row: SysFile) -> UploadedFileOut:
    return UploadedFileOut(
        fileId=row.file_id or 0,
        url=row.url or "",
        fileName=row.file_name or "",
        newFileName=row.new_file_name or "",
        originalFilename=row.original_filename or "",
        size=row.size or 0,
    )


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


async def _store_file(storage: FileStorage, file: UploadFile, current: CurrentUserOut) -> SysFile:
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
    return SysFile(
        original_filename=stored.filename,
        file_name=stored.key,
        new_file_name=Path(stored.key).name,
        url=stored.url,
        file_suffix=ext,
        content_type=file.content_type or "",
        size=stored.size,
        create_by=current.user.user_name,
        create_time=_now(),
    )


async def upload(
    storage: FileStorage,
    db: AsyncSession,
    files: list[UploadFile],
    current: CurrentUserOut,
) -> Result[list[UploadedFileOut]]:
    if not files:
        raise BizException(message="请选择文件", code=ResponseCode.PARAM_ERROR)
    rows = [await _store_file(storage, item, current) for item in files]
    db.add_all(rows)
    await db.commit()
    for row in rows:
        await db.refresh(row)
    return Result.ok(data=[_to_out(row) for row in rows], msg="上传成功")


async def download(
    storage: FileStorage,
    db: AsyncSession,
    *,
    file_id: int | None,
    file_name: str | None,
) -> tuple[bytes, str]:
    key = ""
    name = ""
    if file_id is not None:
        row = await db.get(SysFile, file_id)
        if row is None or row.del_flag != DEL_FLAG_NORMAL:
            raise BizException(message="文件不存在", code=ResponseCode.NOT_FOUND)
        key = row.file_name or ""
        name = row.original_filename or Path(key).name
    elif file_name and file_name.strip():
        key = file_name.strip()
        name = Path(key).name
    else:
        raise BizException(message=ResponseMsg.PARAM_ERROR, code=ResponseCode.PARAM_ERROR)
    if not key:
        raise BizException(message=ResponseMsg.PARAM_ERROR, code=ResponseCode.PARAM_ERROR)
    try:
        data = await storage.read(key)
    except ValueError as exc:
        raise BizException(message=ResponseMsg.PARAM_ERROR, code=ResponseCode.PARAM_ERROR) from exc
    except FileNotFoundError as exc:
        raise BizException(message="文件不存在", code=ResponseCode.NOT_FOUND) from exc
    return data, name
