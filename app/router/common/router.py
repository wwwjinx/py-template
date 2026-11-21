from typing import Annotated

from fastapi import APIRouter, File, Query, UploadFile
from fastapi.responses import Response

from app.router.common import service
from app.storage import FileStorageDep

router = APIRouter(prefix="/common", tags=["文件"])

UploadFilesDep = Annotated[list[UploadFile], File()]


@router.post("/upload")
async def upload(storage: FileStorageDep, files: UploadFilesDep):
    return await service.upload(storage, files)


@router.get("/download")
async def download(
    storage: FileStorageDep,
    file_name: str = Query(..., alias="fileName"),
):
    data, name = await service.download(storage, file_name)
    return Response(
        content=data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )
