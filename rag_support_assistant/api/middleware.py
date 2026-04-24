import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from utils.logger import GetLogger


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)
        self._logger = GetLogger(self.__class__.__name__)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        self._logger.info(
            "Incoming request",
            extra={
                "method": request.method,
                "path": request.url.path
            }
        )

        response = await call_next(request)

        self._logger.info(
            "Outgoing response",
            extra={
                "status_code": response.status_code,
                "path": request.url.path
            }
        )

        return response


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        response.headers["X-Process-Time"] = f"{duration:.4f}"
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)
        self._logger = GetLogger(self.__class__.__name__)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)

        except Exception as ex:
            self._logger.error(
                "Unhandled exception",
                exc_info=True,
                extra={"path": request.url.path}
            )

            return Response(
            content=f'{{"error": "{str(ex)}"}}',
            status_code=500,
            media_type="application/json"
            )