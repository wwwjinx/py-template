"""本地文件存储接口单测试，不依赖数据库。"""

from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.storage.local import LocalFileStorage


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        storage = LocalFileStorage(tmp, url_prefix="/uploads", public_base_url="http://localhost:8001")
        saved = asyncio.run(storage.save(b"hello", filename="hello.txt", content_type="text/plain"))
        _assert(saved.size == 5, f"size: {saved.size}")
        _assert(saved.filename == "hello.txt", f"filename: {saved.filename}")
        _assert(saved.key.endswith(".txt"), f"key: {saved.key}")
        _assert(saved.url.startswith("http://localhost:8001/uploads/"), f"url: {saved.url}")
        _assert((Path(tmp) / saved.key).read_bytes() == b"hello", "file not written")

        data = asyncio.run(storage.read(saved.key))
        _assert(data == b"hello", f"read: {data!r}")
        _assert(storage.url_for(saved.key) == saved.url, "url_for mismatch")

        try:
            asyncio.run(storage.read("../secret.txt"))
            raise AssertionError("traversal should fail")
        except ValueError:
            pass

        asyncio.run(storage.delete(saved.key))
        try:
            asyncio.run(storage.read(saved.key))
            raise AssertionError("deleted file should be missing")
        except FileNotFoundError:
            pass

    print("all tests passed")


if __name__ == "__main__":
    main()
