from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine, text

from app import config

_engine: Engine | None = None


def get_engine() -> Engine:
    """懒加载引擎，导入和启动时不要求 Postgres 已就绪。"""
    global _engine
    if _engine is None:
        if not config.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not set. Add it to env/.dev.env or env/.prod.env.")
        _engine = create_engine(config.DATABASE_URL, pool_pre_ping=True)
    return _engine


def get_db() -> Generator[Session]:
    """FastAPI 依赖：产出一个 SQLModel Session，请求结束时关闭。"""
    with Session(get_engine()) as db:
        yield db


SessionDep = Annotated[Session, Depends(get_db)]


def init_db() -> None:
    """按已声明的 SQLModel 表建表，已存在的表会跳过。需要时手动调用，启动不会自动建表。"""
    from app import models as _models  # noqa: F401

    SQLModel.metadata.create_all(get_engine())


def check_db() -> dict:
    """探测数据库连通性，失败时返回结构化错误而不是把进程打崩。"""
    if not config.DATABASE_URL:
        return {"ok": False, "error": "DATABASE_URL not set"}
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ok": True}
    except Exception as exc:  # noqa: BLE001 — surface as structured failure
        return {"ok": False, "error": str(exc)}
