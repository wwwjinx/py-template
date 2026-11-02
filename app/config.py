from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

APP_ENV = os.getenv("APP_ENV", "dev")
_env_file = Path.cwd() / "env" / (".dev.env" if APP_ENV == "dev" else ".prod.env")
load_dotenv(_env_file)

APP_PORT = int(os.getenv("APP_PORT", "3000"))
APP_NAME = os.getenv("APP_NAME", "py-template")
