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

环境文件在项目根下的 `env/`（`.dev.env` / `.prod.env`），按文件位置解析，不依赖启动时的工作目录。不要把真实密钥写进去。

Docs: http://localhost:8001/docs

---

## Layout

```
app/
  main.py              # create_app + run（打印地址）
  config.py            # 按 APP_ENV 加载 env（相对项目根目录）
  db.py                # SQLModel 异步引擎（懒加载）
  redis_client.py      # Redis 懒连接
  core/                # AppException / BizException
  enums/               # ResponseCode / ResponseMsg（ErrorCode 别名）
  log/                 # stdout + logs/ 滚动文件
  middleware/          # 请求日志 + 全局异常 → Result
  router/              # 汇总；各模块为 router.py（路由）+ service.py（业务）
  models/              # SQLModel 表（示例 Test，对应表 test）
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
| CORS（`CORS_ENABLED` / `CORS_ORIGINS`；`*` 时不开 credentials） | `app/main.py` + config |
| 日志文件 | `logs/all.YYYY-MM-DD.log`（完整流水，含错误）、`logs/error.YYYY-MM-DD.log`（仅错误）；模块日志 `logs/{module}.{id}.YYYY-MM-DD.log`（已 gitignore） |

按模块、按业务 id 写独立文件（不进标准输出和 all 日志）。例如模型原始返回：

```python
from app.log import get_module_logger

get_module_logger("chat", chat_id).info("%s", raw_response)
```

当天直接写到 `logs/chat.{chatId}.2026-11-11.log`。目录可用 `LOG_DIR` 配置；模块日志只保留最近 `LOG_MODULE_CACHE_SIZE` 个打开的文件（默认 256）。

## PostgreSQL

```bash
# optional
docker compose up -d
```

Set in `env/.dev.env`:

```bash
DATABASE_URL=postgresql+psycopg_async://postgres:postgres@localhost:5432/py_template
```

Stack: **SQLModel**（基于 SQLAlchemy 2.x 异步引擎）+ **psycopg3**。引擎懒加载，导入和启动不要求数据库已就绪。需要建表时调用 `await init_db()`（按模型 `create_all`，已存在则跳过），启动不会自动建表。`postgresql://` 与 `postgresql+psycopg://` 会自动改成 `postgresql+psycopg_async://`。

```python
from sqlmodel import select

from app.db import SessionDep
from app.models import Test
from app.utils.result import Result


@router.get("/items")
async def list_items(db: SessionDep):
    result = await db.exec(select(Test))
    return Result.ok(data=result.all())
```

写操作需要自行 `db.commit()`，请求结束只会关闭 session，不会自动提交。



## 登录鉴权与系统管理

已迁入若依常用的登录鉴权、用户/角色/菜单/部门、字典、操作/登录日志，实现按本模板的 FastAPI + SQLModel 异步 Session 习惯，接口路径对齐若依前端。

依赖：`uv sync`（含 `pyjwt`、`bcrypt`）。配置 `DATABASE_URL` 后手动建表并写入超管（启动不会自动执行）：

```bash
uv run python -m app.seed
# 等价：
# uv run python -c "import asyncio; from app.db import init_db; from app.seed import seed_admin; asyncio.run(init_db()); print(asyncio.run(seed_admin()))"
```

默认账号 `admin` / `admin123`。若表里已有 `admin` 用户会跳过，可重复执行。在 `env/.dev.env` 里配置 `JWT_SECRET`（不要提交真实密钥）。

登录示例：

```bash
curl -s -X POST http://localhost:8001/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}'
# 成功：{"code":200,"msg":"登录成功","data":{"token":"..."}}

curl -s http://localhost:8001/getInfo -H "Authorization: Bearer <token>"
curl -s http://localhost:8001/getRouters -H "Authorization: Bearer <token>"
```

常用路径：`POST /login`、`GET /getInfo`、`GET /getRouters`、`POST /logout`；`/system/user`、`/system/role`、`/system/menu`、`/system/dept`、`/system/dict/type`、`/system/dict/data`（含 `GET /system/dict/data/type/{dictType}`）；`/monitor/operlog`、`/monitor/logininfor`。列表在 `data: {rows, total}`。需要登录的接口走 `Authorization: Bearer`。

冒烟测试（临时 sqlite，不改项目真实数据库配置）：

```bash
uv run python tests/test_system_auth.py
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

新模块做成独立包，和 `health`、`test` 一样拆成路由和业务：

```python
# app/router/demo/service.py
from app.utils.result import Result

def ping() -> Result:
    return Result.ok(data={"ok": True})
```

```python
# app/router/demo/router.py
from fastapi import APIRouter

from app.router.demo import service

router = APIRouter(prefix="/demo", tags=["demo"])

@router.get("")
def demo():
    return service.ping()
```

```python
# app/router/demo/__init__.py
from .router import router

__all__ = ["router"]
```

然后在 `app/router/__init__.py` 里 `api_router.include_router(demo.router)`。

`/test` 提供表 `test`（`id` 自增、`text` VARCHAR(255)）的增删改查样例：

- `GET /test` 列表
- `POST /test` 新增，body：`{"text": "..."}`
- `GET /test/{id}` 查询
- `PUT /test/{id}` 更新
- `DELETE /test/{id}` 删除

Demo errors: `GET /test/err`（BizException）、`GET /test/http-err`（HTTPException）。
