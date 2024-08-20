import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = structlog.get_logger()

healthcheck_routes = [
    "/ocrorchestrator",
    "/ocrorchestrator/",
]

api_routes = [
    "/ocrorchestrator/predict",
    "/ocrorchestrator/predict_offline",
]


class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        path = request.url.path
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            method=request.method,
            client_host=request.client.host,
            trans_id=str(uuid.uuid4()),
            api_name=path,
        )

        if request.method == "POST" and path in api_routes:
            request_data = await request.json()
            structlog.contextvars.bind_contextvars(
                guid=request_data.get("guid", ""),
                category=request_data.get("category", ""),
                task=request_data.get("task", ""),
            )

        response = await call_next(request)

        structlog.contextvars.bind_contextvars(
            status_code=response.status_code,
        )

        if path in api_routes:
            if 400 <= response.status_code < 500:
                logger.warn("Client error")
            elif response.status_code >= 500:
                logger.error("Server error")
            else:
                logger.info("OK")

        return response