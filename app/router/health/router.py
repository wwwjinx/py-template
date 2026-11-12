from fastapi import APIRouter

from app.router.health import service

router = APIRouter(tags=["health"], prefix="/health")


@router.get("")
def health():
    return service.ping()


@router.get("/db")
def health_db():
    return service.db()


@router.get("/redis")
def health_redis():
    return service.redis()
