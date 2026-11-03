import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from app import config

_LOG_DIR = Path.cwd() / "logs"
_configured = False


def setup_logging() -> logging.Logger:
    """Configure root app logger: stdout + rotating file under ./logs (like koa log4js)."""
    global _configured
    logger = logging.getLogger("app")
    if _configured:
        return logger

    logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))
    logger.handlers.clear()
    logger.propagate = False

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(fmt)
    logger.addHandler(stream)

    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            _LOG_DIR / "all.log",
            when="midnight",
            backupCount=30,
            encoding="utf-8",
        )
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

        err_handler = TimedRotatingFileHandler(
            _LOG_DIR / "error.log",
            when="midnight",
            backupCount=30,
            encoding="utf-8",
        )
        err_handler.setLevel(logging.ERROR)
        err_handler.setFormatter(fmt)
        logger.addHandler(err_handler)
    except OSError:
        # File logging is best-effort; stdout always works.
        pass

    _configured = True
    return logger


def get_logger(name: str = "app") -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)
