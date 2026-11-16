from fastapi import APIRouter

from app.db import SessionDep
from app.models import TestCreate, TestUpdate
from app.router.test import service

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/err")
def test_err():
    """Demo: business error → Result.fail (HTTP 200, body.code=501)."""
    service.raise_biz()


@router.get("/http-err")
def test_http_err():
    """Demo: HTTPException also wrapped into Result (HTTP 200, body.code)."""
    service.raise_http()


@router.get("")
def list_tests(db: SessionDep):
    return service.list_all(db)


@router.post("")
def create_test(payload: TestCreate, db: SessionDep):
    return service.create(db, payload)


@router.get("/{id}")
def get_test(id: int, db: SessionDep):
    return service.get(db, id)


@router.put("/{id}")
def update_test(id: int, payload: TestUpdate, db: SessionDep):
    return service.update(db, id, payload)


@router.delete("/{id}")
def delete_test(id: int, db: SessionDep):
    return service.delete(db, id)
