from typing import Annotated

from fastapi import APIRouter, File, Query, UploadFile
from fastapi.responses import Response

from app.db import SessionDep
from app.deps import CurrentUserDep
from app.router.common import service
from app.storage import FileStorageDep

router = APIRouter(prefix="/common", tags=["文件"])

UploadFilesDep = Annotated[list[UploadFile], File()]


@router.post("/upload")
async def upload(
    storage: FileStorageDep,
    db: SessionDep,
    files: UploadFilesDep,
    current: CurrentUserDep,
):
    return await service.upload(storage, db, files, current)


@router.get("/download")
async def download(
    storage: FileStorageDep,
    db: SessionDep,
    file_id: int | None = Query(None, alias="fileId"),
    file_name: str | None = Query(None, alias="fileName"),
):
    data, name = await service.download(storage, db, file_id=file_id, file_name=file_name)
    return Response(
        content=data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )
