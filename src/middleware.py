import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .metrics import request_count, request_duration


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()

        response: Response = await call_next(request)

        duration = time.time() - start_time

        # Record metrics
        method = request.method
        endpoint = request.url.path
        status = response.status_code

        request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)

        return response
