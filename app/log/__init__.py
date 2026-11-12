import logging
import re
import sys
import threading
from collections import OrderedDict
from datetime import date
from pathlib import Path

from app import config

_FORMATTER = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")
_DATED_LOG = re.compile(r"^(.+)\.log\.(\d{4}-\d{2}-\d{2})$")
_setup_lock = threading.Lock()
_module_lock = threading.Lock()
_configured = False
# 最近使用的模块 logger；淘汰时关闭文件句柄，避免业务 id 过多占满 fd
_module_loggers: OrderedDict[str, logging.Logger] = OrderedDict()

__all__ = ["get_logger", "get_module_logger", "setup_logging"]


def _log_level() -> int:
    return getattr(logging, config.LOG_LEVEL, logging.INFO)


def _log_dir() -> Path:
    path = Path(config.LOG_DIR)
    return path if path.is_absolute() else config.PROJECT_ROOT / path


def _safe_part(value: str, field: str) -> str:
    """把模块名或业务 id 清洗成可用于文件名的安全片段。"""
    cleaned = _UNSAFE.sub("_", (value or "").strip()).strip("._")
    if not cleaned:
        raise ValueError(f"{field} must be a non-empty filename-safe value")
    return cleaned


def _close_handlers(logger: logging.Logger) -> None:
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()


class _DatedFileHandler(logging.FileHandler):
    """当天直接写到 `{stem}.log.YYYY-MM-DD`，跨天自动换文件，并只保留 backupCount 天。"""

    def __init__(
        self,
        directory: Path,
        stem: str,
        *,
        backup_count: int = 30,
        encoding: str = "utf-8",
    ) -> None:
        self._directory = directory
        self._stem = stem
        self._backup_count = backup_count
        self._current_day = self._today()
        directory.mkdir(parents=True, exist_ok=True)
        super().__init__(self._path_for(self._current_day), encoding=encoding, delay=True)

    @staticmethod
    def _today() -> str:
        return date.today().isoformat()

    def _path_for(self, day: str) -> Path:
        return self._directory / f"{self._stem}.log.{day}"

    def _prune(self) -> None:
        if self._backup_count <= 0:
            return
        files = {
            p
            for p in self._directory.glob(f"{self._stem}.log.*")
            if _DATED_LOG.fullmatch(p.name) and p.name.startswith(f"{self._stem}.log.")
        }
        # 把即将写入的当天文件也计入保留额度，避免跨天时多留一份
        files.add(Path(self.baseFilename))
        for path in sorted(files, key=lambda p: p.name)[: -self._backup_count]:
            path.unlink(missing_ok=True)

    def _rollover(self, day: str) -> None:
        if self.stream:
            self.stream.close()
            self.stream = None
        self._current_day = day
        self.baseFilename = str(self._path_for(day))
        self._prune()

    def emit(self, record: logging.LogRecord) -> None:
        day = self._today()
        if day != self._current_day:
            self._rollover(day)
        super().emit(record)


def _add_dated_handler(
    logger: logging.Logger,
    stem: str,
    *,
    level: int | None = None,
) -> bool:
    """挂上按日期命名的文件；失败时返回 False，不打断已有 handler。"""
    try:
        handler = _DatedFileHandler(_log_dir(), stem, backup_count=30)
        handler.setFormatter(_FORMATTER)
        if level is not None:
            handler.setLevel(level)
        logger.addHandler(handler)
        return True
    except OSError:
        return False


def setup_logging() -> logging.Logger:
    """配置根日志：标准输出 + 按日期的 all / error 文件。目录由 LOG_DIR 决定。

    `all.log.YYYY-MM-DD` 是完整流水，因此会包含 error；
    `error.log.YYYY-MM-DD` 只筛 ERROR 及以上，方便单独查看。
    """
    global _configured
    logger = logging.getLogger("app")
    if _configured:
        return logger
    with _setup_lock:
        if _configured:
            return logger
        logger.setLevel(_log_level())
        _close_handlers(logger)
        logger.propagate = False

        stream = logging.StreamHandler(sys.stdout)
        stream.setFormatter(_FORMATTER)
        logger.addHandler(stream)

        _add_dated_handler(logger, "all")
        _add_dated_handler(logger, "error", level=logging.ERROR)
        _configured = True
    return logger


def get_logger(name: str = "app") -> logging.Logger:
    """获取指定名称的 logger，首次调用时会初始化日志配置。"""
    setup_logging()
    return logging.getLogger(name)


def get_module_logger(module: str, key: str) -> logging.Logger:
    """按模块和业务 id 写独立文件 `logs/{module}.{key}.log.YYYY-MM-DD`。

    不进标准输出和 all 日志。只保留最近使用的一批打开文件
    （`LOG_MODULE_CACHE_SIZE`，默认 256），避免 chat_id 很多时占满文件描述符。
    """
    setup_logging()
    module = _safe_part(module, "module")
    key = _safe_part(key, "key")
    name = f"app.{module}.{key}"

    with _module_lock:
        existing = _module_loggers.get(name)
        if existing is not None and existing.handlers:
            _module_loggers.move_to_end(name)
            return existing

        logger = logging.getLogger(name)
        logger.setLevel(_log_level())
        logger.propagate = False
        if not logger.handlers and not _add_dated_handler(logger, f"{module}.{key}"):
            # 写文件失败时退到标准输出，避免日志被丢掉
            stream = logging.StreamHandler(sys.stdout)
            stream.setFormatter(_FORMATTER)
            logger.addHandler(stream)

        limit = config.LOG_MODULE_CACHE_SIZE
        if name in _module_loggers:
            _module_loggers.move_to_end(name)
        else:
            while len(_module_loggers) >= limit:
                _, old_logger = _module_loggers.popitem(last=False)
                _close_handlers(old_logger)
            _module_loggers[name] = logger
        return logger
