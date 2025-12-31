import datetime
from typing import Callable, Optional, Dict, Any
from django.http import HttpRequest, HttpResponse
import structlog

logger = structlog.get_logger(__name__)


class RequestResponseLoggerMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        self.log_request(request)
        response = self.get_response(request)
        self.log_response(request, response)
        return response

    def log_request(self, request: HttpRequest):
        try:
            logger.info(
                "request_received",
                method=request.method,
                path=request.path,
                query_params=dict(request.GET),
                headers={k: v for k, v in request.headers.items()},
                body=request.body.decode("utf-8") if request.body else None,
                timestamp=str(datetime.datetime.now())
            )
        except Exception as e:
            logger.error("failed_logging_request", error=str(e))

    def log_response(
        self, request: HttpRequest, response: HttpResponse, additional_info: Optional[Dict] = None
    ):
        try:
            logger.info(
                "response_generated",
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                headers=dict(response.items()),
                body=response.content.decode("utf-8") if response.content else None,
                timestamp=str(datetime.datetime.now()),
                **(additional_info or {})
            )
        except Exception as e:
            logger.error("failed_logging_response", error=str(e))
