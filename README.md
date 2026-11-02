# FastAPI backend template

Requires **Python 3.12+**. Use [mise](https://mise.jdx.dev/) (or similar) for the Python version, and [uv](https://github.com/astral-sh/uv) for deps — like nvm + pnpm.

```bash
uv sync
uv run uvicorn app.main:app --reload --port 8001
```

Prod-style:

```bash
APP_ENV=prod uv run uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Without uv (fallback):

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8001
```

Environment files live in `env/` (`.dev.env` / `.prod.env`). Do not put real secrets there.

Docs: http://localhost:8001/docs

---

## Layout

```
app/
  main.py          # FastAPI entry
  config.py        # load env by APP_ENV
  db.py            # SQLAlchemy engine + get_db (lazy)
  router/          # APIRouter modules
env/
  .dev.env
  .prod.env
```

## PostgreSQL

Set `DATABASE_URL` in `env/.dev.env` (or `.prod.env`):

```bash
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/dbname
```

Stack: **SQLAlchemy 2.x** + **psycopg3** (`psycopg[binary]`). The engine is created lazily on first use, so importing / starting the app does **not** require a live database.

In a route:

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db

@router.get("/items")
def list_items(db: Session = Depends(get_db)):
    ...
```

Optional check: `GET /health/db` → `{"ok": true}` or `{"ok": false, "error": "..."}`.

## Add a route

```python
# app/router/demo.py
from fastapi import APIRouter

router = APIRouter(prefix="/demo", tags=["demo"])

@router.get("")
async def demo():
    return {"ok": True}
```

Then `app.include_router(demo.router)` in `app/main.py`.
