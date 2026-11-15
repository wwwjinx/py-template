from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, text
from sqlmodel.ext.asyncio.session import AsyncSession

from app import config

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """懒加载异步引擎，导入和启动时不要求 Postgres 已就绪。"""
    global _engine
    if _engine is None:
        if not config.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not set. Add it to env/.dev.env or env/.prod.env.")
        _engine = create_async_engine(config.DATABASE_URL, pool_pre_ping=True)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession]:
    """FastAPI 依赖：产出一个异步 Session，请求结束时关闭。"""
    async with get_session_factory()() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def init_db() -> None:
    """按已声明的 SQLModel 表建表，已存在的表会跳过。需要时手动调用，启动不会自动建表。"""
    from app import models as _models  # noqa: F401

    async with get_engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def check_db() -> dict:
    """探测数据库连通性，失败时返回结构化错误而不是把进程打崩。"""
    if not config.DATABASE_URL:
        return {"ok": False, "error": "DATABASE_URL not set"}
    try:
        async with get_engine().connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"ok": True}
    except Exception as exc:  # noqa: BLE001 — surface as structured failure
        return {"ok": False, "error": str(exc)}
