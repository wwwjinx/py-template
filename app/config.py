from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

APP_ENV = os.getenv("APP_ENV", "dev")
_env_file = Path.cwd() / "env" / (".dev.env" if APP_ENV == "dev" else ".prod.env")
load_dotenv(_env_file)

APP_PORT = int(os.getenv("APP_PORT", "8001"))
APP_NAME = os.getenv("APP_NAME", "py-template")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
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
