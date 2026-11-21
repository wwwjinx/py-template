"""登录鉴权与系统管理接口的冒烟测试。使用临时 sqlite，不碰项目真实 DATABASE_URL。"""

from __future__ import annotations

import asyncio
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@contextmanager
def _temp_db() -> Iterator[None]:
    import app.config as cfg
    import app.db as dbmod

    previous_url = cfg.DATABASE_URL
    previous_secret = cfg.JWT_SECRET
    previous_storage = cfg.STORAGE_LOCAL_DIR
    previous_engine = dbmod._engine
    previous_factory = dbmod._session_factory

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)
    upload_dir = Path(tempfile.mkdtemp())
    dbmod._engine = None
    dbmod._session_factory = None
    cfg.DATABASE_URL = f"sqlite+aiosqlite:///{db_path.as_posix()}"
    cfg.JWT_SECRET = "test-jwt-secret-do-not-use-32b+"
    cfg.JWT_EXPIRE_MINUTES = 60
    cfg.STORAGE_BACKEND = "local"
    cfg.STORAGE_LOCAL_DIR = str(upload_dir)
    cfg.STORAGE_PUBLIC_BASE_URL = ""
    try:
        yield
    finally:
        engine = dbmod._engine
        dbmod._engine = previous_engine
        dbmod._session_factory = previous_factory
        cfg.DATABASE_URL = previous_url
        cfg.JWT_SECRET = previous_secret
        cfg.STORAGE_LOCAL_DIR = previous_storage
        if engine is not None:
            asyncio.run(engine.dispose())
        db_path.unlink(missing_ok=True)
        for child in upload_dir.rglob("*"):
            if child.is_file():
                child.unlink(missing_ok=True)
        for child in sorted(upload_dir.rglob("*"), reverse=True):
            if child.is_dir():
                child.rmdir()
        upload_dir.rmdir()


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    with _temp_db():
        from fastapi.testclient import TestClient

        from app.db import init_db
        from app.main import app
        from app.seed import seed_admin

        asyncio.run(init_db())
        result = asyncio.run(seed_admin())
        _assert("seeded" in result, f"first seed should insert admin, got {result!r}")
        skipped = asyncio.run(seed_admin())
        _assert("skipped" in skipped, f"second seed should be reentrant, got {skipped!r}")

        with TestClient(app) as client:
            bad = client.post("/login", json={"username": "admin", "password": "wrong"})
            _assert(bad.status_code == 200, f"http status should stay 200, got {bad.status_code}")
            _assert(bad.json()["code"] == 401, f"wrong password should be 401, got {bad.json()}")

            no_token = client.get("/getInfo")
            _assert(no_token.status_code == 200, f"getInfo http={no_token.status_code}")
            _assert(
                no_token.json()["code"] == 401,
                f"getInfo without token should be 401, got {no_token.json()}",
            )

            no_routers = client.get("/getRouters")
            _assert(
                no_routers.json()["code"] == 401,
                f"getRouters without token should be 401, got {no_routers.json()}",
            )

            root = client.get("/")
            _assert(root.status_code == 200 and root.json()["code"] == 200, f"public /: {root.json()}")
            health = client.get("/health")
            _assert(health.status_code == 200, f"public /health http={health.status_code}")

            no_test = client.get("/test")
            _assert(no_test.status_code == 200, f"/test http={no_test.status_code}")
            _assert(
                no_test.json()["code"] == 401,
                f"/test without token should be 401, got {no_test.json()}",
            )

            ok = client.post("/login", json={"username": "admin", "password": "admin123"})
            body = ok.json()
            _assert(body["code"] == 200, f"login should succeed, got {body}")
            _assert(body["msg"] == "登录成功", f"login msg, got {body}")
            token = body["data"]["token"]
            _assert(isinstance(token, str) and token, f"missing token: {body}")

            headers = {"Authorization": f"Bearer {token}"}

            no_upload = client.post("/common/upload", files={"files": ("hello.txt", b"hello", "text/plain")})
            _assert(no_upload.status_code == 200, f"upload http={no_upload.status_code}")
            _assert(
                no_upload.json()["code"] == 401,
                f"upload without token should be 401, got {no_upload.json()}",
            )

            uploaded = client.post(
                "/common/upload",
                headers=headers,
                files={"files": ("hello.txt", b"hello", "text/plain")},
            ).json()
            _assert(uploaded["code"] == 200, f"upload failed: {uploaded}")
            _assert(len(uploaded["data"]) == 1, f"single upload should return one item: {uploaded}")
            item = uploaded["data"][0]
            _assert(item["originalFilename"] == "hello.txt", f"name: {uploaded}")
            _assert(item["size"] == 5, f"size: {uploaded}")
            file_id = item["fileId"]
            _assert(isinstance(file_id, int) and file_id > 0, f"fileId: {uploaded}")
            file_key = item["fileName"]
            file_url = item["url"]
            _assert(file_url.startswith("/uploads/"), f"url: {file_url}")
            static = client.get(file_url)
            _assert(static.status_code == 200 and static.content == b"hello", f"static {file_url}: {static.status_code}")
            downloaded = client.get("/common/download", headers=headers, params={"fileId": file_id})
            _assert(downloaded.status_code == 200 and downloaded.content == b"hello", f"download by fileId: {downloaded.status_code}")
            downloaded_by_name = client.get("/common/download", headers=headers, params={"fileName": file_key})
            _assert(downloaded_by_name.status_code == 200 and downloaded_by_name.content == b"hello", f"download by fileName: {downloaded_by_name.status_code}")
            missing = client.get("/common/download", headers=headers, params={"fileId": 999999}).json()
            _assert(missing["code"] == 404, f"missing fileId should be 404, got {missing}")

            rejected = client.post(
                "/common/upload",
                headers=headers,
                files={"files": ("bad.exe", b"MZ", "application/octet-stream")},
            ).json()
            _assert(rejected["code"] == 400, f"exe should be rejected: {rejected}")

            many = client.post(
                "/common/upload",
                headers=headers,
                files=[
                    ("files", ("hello.txt", b"hello", "text/plain")),
                    ("files", ("world.txt", b"world", "text/plain")),
                ],
            ).json()
            _assert(many["code"] == 200, f"multi upload failed: {many}")
            _assert(len(many["data"]) == 2, f"multi upload count: {many}")
            names = [row["originalFilename"] for row in many["data"]]
            _assert(names == ["hello.txt", "world.txt"], f"multi names: {many}")
            _assert(many["data"][0]["size"] == 5 and many["data"][1]["size"] == 5, f"multi size: {many}")
            ids = [row["fileId"] for row in many["data"]]
            _assert(all(isinstance(i, int) and i > 0 for i in ids), f"multi fileId: {many}")
            _assert(len(set(ids)) == 2, f"multi fileId should be unique: {many}")

            info = client.get("/getInfo", headers=headers).json()
            _assert(info["code"] == 200, f"getInfo failed: {info}")
            _assert(info["data"]["user"]["userName"] == "admin", f"userName: {info['data']}")
            _assert(
                "*:*:*" in info["data"]["permissions"],
                f"super admin perms: {info['data']['permissions']}",
            )
            _assert("admin" in info["data"]["roles"], f"roles: {info['data']['roles']}")

            routers = client.get("/getRouters", headers=headers).json()
            _assert(routers["code"] == 200, f"getRouters failed: {routers}")
            paths = [item.get("path") for item in routers["data"]]
            _assert("/system" in paths, f"expected /system in routers, got {routers['data']}")
            system = next(item for item in routers["data"] if item.get("path") == "/system")
            child_paths = [c.get("path") for c in system.get("children") or []]
            _assert("user" in child_paths, f"expected user menu, got {system}")

            users = client.get("/system/user/list", headers=headers).json()
            _assert(users["code"] == 200, f"user list failed: {users}")
            _assert(users["data"]["total"] >= 1, f"user total: {users}")
            _assert(any(r["userName"] == "admin" for r in users["data"]["rows"]), f"rows: {users}")

            depts = client.get("/system/dept/list", headers=headers).json()
            _assert(depts["code"] == 200 and len(depts["data"]) >= 1, f"dept list: {depts}")

            roles = client.get("/system/role/list", headers=headers).json()
            _assert(roles["code"] == 200 and roles["data"]["total"] >= 1, f"role list: {roles}")

            created = client.post(
                "/system/dept/",
                headers=headers,
                json={"parentId": 100, "deptName": "测试部门", "orderNum": 9, "status": "0"},
            ).json()
            _assert(created["code"] == 200, f"create dept: {created}")
            new_id = created["data"]["deptId"]
            deleted = client.delete(f"/system/dept/{new_id}", headers=headers).json()
            _assert(deleted["code"] == 200, f"delete dept: {deleted}")

            sex = client.get("/system/dict/data/type/sys_user_sex", headers=headers).json()
            _assert(sex["code"] == 200, f"dict by type: {sex}")
            labels = [item["dictLabel"] for item in sex["data"]]
            _assert("男" in labels, f"dict labels: {sex}")

            logs = client.get("/monitor/logininfor/list", headers=headers).json()
            _assert(logs["code"] == 200 and logs["data"]["total"] >= 1, f"login logs: {logs}")

            oper = client.get("/monitor/operlog/list", headers=headers).json()
            _assert(oper["code"] == 200, f"oper logs: {oper}")
            _assert("rows" in oper["data"] and "total" in oper["data"], f"page shape: {oper}")

            logout = client.post("/logout", headers=headers).json()
            _assert(logout["code"] == 200, f"logout: {logout}")

        print("all tests passed")


if __name__ == "__main__":
    main()
