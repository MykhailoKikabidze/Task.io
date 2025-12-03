import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

logger = logging.getLogger("app_logger")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        url = request.url.path

        logger.info(f"Incoming request: {method} {url}")
        response: Response = await call_next(request)

        duration = time.time() - start_time
        logger.info(f"Request {method} {url} completed in {duration:.2f}s with status {response.status_code}")
        return response
