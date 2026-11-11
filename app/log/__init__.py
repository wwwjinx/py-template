import logging
import re
import sys
import threading
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from app import config

_LOG_DIR = Path.cwd() / "logs"
_configured = False
_module_lock = threading.Lock()
_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")
_FORMATTER = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

__all__ = ["get_logger", "get_module_logger", "setup_logging"]


def _safe_part(value: str, field: str) -> str:
    cleaned = _UNSAFE.sub("_", (value or "").strip()).strip("._")
    if not cleaned:
        raise ValueError(f"{field} must be a non-empty filename-safe value")
    return cleaned


def setup_logging() -> logging.Logger:
    """Configure root app logger: stdout + rotating file under ./logs (like koa log4js)."""
    global _configured
    logger = logging.getLogger("app")
    if _configured:
        return logger

    logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))
    logger.handlers.clear()
    logger.propagate = False

    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(_FORMATTER)
    logger.addHandler(stream)

    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            _LOG_DIR / "all.log",
            when="midnight",
            backupCount=30,
            encoding="utf-8",
        )
        file_handler.setFormatter(_FORMATTER)
        logger.addHandler(file_handler)

        err_handler = TimedRotatingFileHandler(
            _LOG_DIR / "error.log",
            when="midnight",
            backupCount=30,
            encoding="utf-8",
        )
        err_handler.setLevel(logging.ERROR)
        err_handler.setFormatter(_FORMATTER)
        logger.addHandler(err_handler)
    except OSError:
        # File logging is best-effort; stdout always works.
        pass

    _configured = True
    return logger


def get_logger(name: str = "app") -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)


def get_module_logger(module: str, key: str) -> logging.Logger:
    """Write only to logs/{module}.{key}.log, rotated daily.

    Rollover files look like logs/chat.{chatId}.log.2026-11-11.
    Records do not go to stdout or all.log.
    """
    setup_logging()
    module = _safe_part(module, "module")
    key = _safe_part(key, "key")
    logger = logging.getLogger(f"app.{module}.{key}")
    if logger.handlers:
        return logger

    with _module_lock:
        if logger.handlers:
            return logger
        logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))
        logger.propagate = False
        try:
            _LOG_DIR.mkdir(parents=True, exist_ok=True)
            handler = TimedRotatingFileHandler(
                _LOG_DIR / f"{module}.{key}.log",
                when="midnight",
                backupCount=30,
                encoding="utf-8",
            )
            handler.setFormatter(_FORMATTER)
            logger.addHandler(handler)
        except OSError:
            pass
    return logger
