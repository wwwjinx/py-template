from fastapi import APIRouter

from app.router.test import service

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/xx")
def test_xx():
    return service.xx()


@router.get("/err")
def test_err():
    """Demo: business error → Result.fail (HTTP 200, body.code=501)."""
    service.raise_biz()


@router.get("/http-err")
def test_http_err():
    """Demo: HTTPException also wrapped into Result (HTTP 200, body.code)."""
    service.raise_http()


@router.get("/{name}")
def test_name(name: str):
    return service.by_name(name)
