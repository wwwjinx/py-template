import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.log import get_logger

logger = get_logger("app.access")


class RequestLogMiddleware(BaseHTTPMiddleware):
    """Log method / path / status / duration (koa loggerMiddleware equivalent)."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            ms = (time.perf_counter() - start) * 1000
            status = response.status_code if response is not None else 500
            client = request.client.host if request.client else "-"
            logger.info(
                "%s %s %s - %s - %.1fms",
                request.method,
                status,
                request.url.path,
                client,
                ms,
            )
