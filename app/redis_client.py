from urllib.parse import quote

from redis import Redis

from app import config

_client: Redis | None = None


def _build_url() -> str:
    if config.REDIS_URL:
        return config.REDIS_URL
    user = config.REDIS_USERNAME
    password = config.REDIS_PASSWORD
    host = config.REDIS_HOST or "127.0.0.1"
    port = config.REDIS_PORT
    db = config.REDIS_DB
    if user and password:
        auth = f"{quote(user, safe='')}:{quote(password, safe='')}@"
    elif password:
        auth = f":{quote(password, safe='')}@"
    elif user:
        auth = f"{quote(user, safe='')}@"
    else:
        auth = ""
    return f"redis://{auth}{host}:{port}/{db}"


def redis_configured() -> bool:
    return bool(config.REDIS_URL or config.REDIS_HOST)


def get_redis() -> Redis:
    """Lazy Redis client: import/startup does not require a live Redis."""
    global _client
    if _client is None:
        if not redis_configured():
            raise RuntimeError(
                "Redis is not configured. Set REDIS_URL or REDIS_HOST in env/.dev.env."
            )
        _client = Redis.from_url(
            _build_url(),
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
    return _client


def check_redis() -> dict:
    """Light connectivity check; never raises to the caller as an unhandled crash."""
    if not redis_configured():
        return {"ok": False, "error": "Redis not configured (REDIS_URL / REDIS_HOST)"}
    try:
        client = get_redis()
        pong = client.ping()
        return {"ok": True, "pong": bool(pong)}
    except Exception as exc:  # noqa: BLE001 — surface as structured failure
        return {"ok": False, "error": str(exc)}
