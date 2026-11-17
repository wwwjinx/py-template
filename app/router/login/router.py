from fastapi import APIRouter, Request

from app.db import SessionDep
from app.deps import CurrentUserDep
from app.router.login import service
from app.schemas.login import LoginBody

public_router = APIRouter(tags=["登录"])
router = APIRouter(tags=["登录"])


@public_router.post("/login")
async def login(payload: LoginBody, db: SessionDep, request: Request):
    return await service.login(db, payload.username, payload.password, request)


@router.get("/getInfo")
async def get_info(db: SessionDep, current: CurrentUserDep):
    return await service.get_info(db, current)


@router.get("/getRouters")
async def get_routers(db: SessionDep, current: CurrentUserDep):
    return await service.get_routers(db, current)


@router.post("/logout")
async def logout(db: SessionDep, current: CurrentUserDep, request: Request):
    return await service.logout(db, current, request)
