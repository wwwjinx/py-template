import os
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录（含 pyproject.toml / env/），不依赖启动时的 cwd
PROJECT_ROOT = Path(__file__).resolve().parent.parent

APP_ENV = os.getenv("APP_ENV", "dev")
_env_file = PROJECT_ROOT / "env" / (".dev.env" if APP_ENV == "dev" else ".prod.env")
load_dotenv(_env_file)

APP_PORT = int(os.getenv("APP_PORT", "8001"))
APP_NAME = os.getenv("APP_NAME", "py-template")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = os.getenv("LOG_DIR", "logs")
try:
    LOG_MODULE_CACHE_SIZE = max(1, int(os.getenv("LOG_MODULE_CACHE_SIZE", "256")))
except ValueError:
    LOG_MODULE_CACHE_SIZE = 256
CORS_ENABLED = os.getenv("CORS_ENABLED", "true").lower() in {"1", "true", "yes", "on"}
_cors_raw = os.getenv("CORS_ORIGINS", "*").strip()
CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()] or ["*"]

# Example: postgresql+psycopg://user:pass@localhost:5432/dbname
_raw_db = os.getenv("DATABASE_URL", "").strip()
if _raw_db.startswith("postgresql://") and "+psycopg" not in _raw_db:
    DATABASE_URL = "postgresql+psycopg://" + _raw_db[len("postgresql://") :]
else:
    DATABASE_URL = _raw_db

IS_DEV = APP_ENV == "dev"

# Redis: REDIS_URL wins; otherwise build from host/port/password/db
REDIS_URL = os.getenv("REDIS_URL", "").strip()
REDIS_HOST = os.getenv("REDIS_HOST", "").strip()
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "").strip()
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_USERNAME = os.getenv("REDIS_USERNAME", "").strip()
