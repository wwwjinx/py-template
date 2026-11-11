# FastAPI backend template

麻雀虽小，五脏俱全 — FastAPI + uv，分层对齐同级 `koa-ts-template`。

Requires **Python 3.15+**. Use [mise](https://mise.jdx.dev/) for the Python version, and [uv](https://github.com/astral-sh/uv) for deps (nvm + pnpm 思路).

```bash
uv sync
uv run dev                 # 读 env APP_PORT（默认 8001），启动时打印 local URL
# 等价：
uv run python -m app.main
```

Prod-style:

```bash
APP_ENV=prod uv run start
```

Without uv (fallback):

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
python -m app.main
```

Environment files live in `env/` (`.dev.env` / `.prod.env`). Do not put real secrets there.

Docs: http://localhost:8001/docs

---

## Layout

```
app/
  main.py              # create_app + run（打印地址）
  config.py            # 按 APP_ENV 加载 env
  db.py                # SQLAlchemy 懒连接
  redis_client.py      # Redis 懒连接
  core/                # AppException / BizException
  enums/               # ResponseCode / ResponseMsg（ErrorCode 别名）
  log/                 # stdout + logs/ 滚动文件
  middleware/          # 请求日志 + 全局异常 → Result
  router/              # APIRouter 汇总
  utils/               # Result、get_ip_address
env/
  .dev.env
  .prod.env
docker-compose.yml     # 可选：Postgres + Redis
```

## Response shape（对齐若依）

所有业务响应用 `Result`：

```json
{"code": 200, "msg": "success", "data": ...}
```

- 成功：`Result.ok(data=...)`
- 失败：`Result.fail(msg=..., code=...)` 或 `raise BizException(...)` / `HTTPException`
- **HTTP 状态**：**HTTP 200**，语义放在 **body.code**（含 404 / 校验错误 / 未捕获异常）
- `/health/db`、`/health/redis` 无服务或连不上时仍返回 Result.fail，进程不崩

## Middleware / 横切

| 能力 | 位置 |
|------|------|
| 请求日志（方法/路径/状态/耗时） | `app/middleware/request_log.py` |
| 全局异常 → Result | `app/middleware/exception.py` |
| CORS（`CORS_ENABLED` / `CORS_ORIGINS`） | `app/main.py` + config |
| 日志文件 | `logs/all.log`、`logs/error.log`；模块日志 `logs/{module}.{id}.log`（已 gitignore） |

按模块、按业务 id 写独立文件（不进标准输出和 `all.log`）。例如模型原始返回：

```python
from app.log import get_module_logger

get_module_logger("chat", chat_id).info("%s", raw_response)
```

文件是 `logs/chat.{chatId}.log`，按天滚动为 `logs/chat.{chatId}.log.2026-11-11`。

## PostgreSQL

```bash
# optional
docker compose up -d
```

Set in `env/.dev.env`:

```bash
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/py_template
```

Stack: **SQLAlchemy 2.x** + **psycopg3**. Engine is lazy — import / start does **not** need a live DB.

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db

@router.get("/items")
def list_items(db: Session = Depends(get_db)):
    ...
```


## Redis

Stack: **redis-py**（可选 hiredis）. Client is lazy — import / start does **not** need a live Redis.

In `env/.dev.env` (placeholders only; put real password in a local override or export, never commit secrets):

```bash
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
# or: REDIS_URL=redis://:your_password@127.0.0.1:6379/0
```

```python
from app.redis_client import get_redis

r = get_redis()
r.set("k", "v")
```

Health: `GET /health/redis` → `Result.ok` / `Result.fail`.

Optional: `docker compose up -d redis` (compose image has no password by default).

## Add a route

Put a router in its own package, same shape as `health` and `test`:

```python
# app/router/demo/service.py
from fastapi import APIRouter
from app.utils.result import Result

router = APIRouter(prefix="/demo", tags=["demo"])

@router.get("")
async def demo():
    return Result.ok(data={"ok": True})
```

```python
# app/router/demo/__init__.py
from .service import router

__all__ = ["router"]
```

Then `api_router.include_router(demo.router)` in `app/router/__init__.py`.

Demo errors: `GET /test/err`（BizException）、`GET /test/http-err`（HTTPException）。
