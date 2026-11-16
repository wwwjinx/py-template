from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.exceptions import BizException
from app.enums import ResponseCode, ResponseMsg
from app.models import Test, TestCreate, TestUpdate
from app.utils.result import Result


def raise_biz() -> None:
    raise BizException(message="test error", code=501)


def raise_http() -> None:
    raise HTTPException(status_code=401, detail="unauthorized")


def list_all(db: Session) -> Result[list[Test]]:
    return Result.ok(data=db.exec(select(Test).order_by(Test.id)).all())


def get(db: Session, id: int) -> Result[Test]:
    row = db.get(Test, id)
    if row is None:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    return Result.ok(data=row)


def create(db: Session, payload: TestCreate) -> Result[Test]:
    row = Test.model_validate(payload)
    db.add(row)
    db.commit()
    db.refresh(row)
    return Result.ok(data=row)


def update(db: Session, id: int, payload: TestUpdate) -> Result[Test]:
    row = db.get(Test, id)
    if row is None:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    row.sqlmodel_update(payload.model_dump(exclude_unset=True))
    db.add(row)
    db.commit()
    db.refresh(row)
    return Result.ok(data=row)


def delete(db: Session, id: int) -> Result[None]:
    row = db.get(Test, id)
    if row is None:
        raise BizException(message=ResponseMsg.NOT_FOUND, code=ResponseCode.NOT_FOUND)
    db.delete(row)
    db.commit()
    return Result.ok(data=None)
