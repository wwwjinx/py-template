# FastAPI backend template

Requires **Python 3.12+**. Prefer [uv](https://github.com/astral-sh/uv) or pip + venv.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

uvicorn app.main:app --reload --port 3000   # APP_ENV=dev (default)
APP_ENV=prod uvicorn app.main:app --host 0.0.0.0 --port 3000
```

Environment files live in `env/` (`.dev.env` / `.prod.env`). Do not put real secrets there.

Docs: http://localhost:3000/docs

---

## Layout

```
app/
  main.py          # FastAPI entry
  config.py        # load env by APP_ENV
  router/          # APIRouter modules
env/
  .dev.env
  .prod.env
```

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
