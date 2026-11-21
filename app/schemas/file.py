from pydantic import BaseModel, Field


class UploadedFileOut(BaseModel):
    fileId: int
    url: str
    fileName: str
    newFileName: str
    originalFilename: str
    size: int = Field(ge=0)
