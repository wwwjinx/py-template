from collections.abc import Generator
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app import config

_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker[Session]] = None


def get_engine() -> Engine:
    """Lazy engine: import/startup does not require a live Postgres."""
    global _engine, _SessionLocal
    if _engine is None:
        if not config.DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL is not set. Add it to env/.dev.env or env/.prod.env."
            )
        _engine = create_engine(
            config.DATABASE_URL,
            pool_pre_ping=True,
        )
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a SQLAlchemy Session."""
    get_engine()
    assert _SessionLocal is not None
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db() -> dict:
    """Light connectivity check; never raises to the caller as an unhandled crash."""
    if not config.DATABASE_URL:
        return {"ok": False, "error": "DATABASE_URL not set"}
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ok": True}
    except Exception as exc:  # noqa: BLE001 — surface as structured failure
        return {"ok": False, "error": str(exc)}
