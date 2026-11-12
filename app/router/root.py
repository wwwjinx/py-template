from fastapi import APIRouter

from app import config
from app.utils.result import Result

router = APIRouter(tags=["root"])


@router.get("/")
def root():
    return Result.ok(data={"message": "ok", "app": config.APP_NAME})
