import logging
import time
from datetime import datetime
from logging import LogRecord
from typing import Dict, Optional, Any

from pythonjsonlogger import jsonlogger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


# JSON Formatter for structured logging
class UtcJsonFormatter(jsonlogger.JsonFormatter):
    converter = datetime.utcfromtimestamp

    def formatTime(self, record: LogRecord, datefmt: Optional[str] = None) -> str:
        ct = self.converter(record.created)  # type: ignore
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%dT%H:%M:%S")
            s = "%s.%03dZ" % (t, record.msecs)
        return s


# Access log middleware
class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        response: Response = await call_next(request)
        process_time = time.time() - start_time
        path = request.scope["path"]
        ignored = {"/status", "/metrics"}
        if path not in ignored:
            access_logger = logging.getLogger("access")
            access_logger.info(
                {
                    "req": {
                        "id": request.headers.get("x-amzn-trace-id", "MISSING"),
                        "method": request.method,
                        "query_string": request.scope["query_string"].decode("utf-8"),
                        "path": request.scope["path"],
                    },
                    "res": {
                        "length_bytes": int(response.headers.get("content-length", 0)),
                        "duration_ms": round(process_time * 1000, 1),
                        "status": response.status_code,
                    },
                }
            )
        return response


# Logging configuration
def get_dev_config() -> Dict[str, Any]:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {"handlers": ["console"], "level": "DEBUG"},
        "formatters": {
            "dev": {
                "format": "[%(levelname)s] %(asctime)s (%(name)s) %(message)s",
                "datefmt": "%H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "dev",
            },
        },
    }


def get_prod_config() -> Dict[str, Any]:
    return {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "json_access": {
                "()": "app.logging.UtcJsonFormatter",
                "format": "%(asctime)s %(levelname)s %(name)s",
                "rename_fields": {"asctime": "timestamp", "levelname": "level"},
            },
            "json": {
                "()": "app.logging.UtcJsonFormatter",
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                "rename_fields": {"asctime": "timestamp", "levelname": "level"},
            },
        },
        "handlers": {
            "json_access": {
                "class": "logging.StreamHandler",
                "formatter": "json_access",
            },
            "json": {
                "class": "logging.StreamHandler",
                "formatter": "json",
            },
        },
        "loggers": {
            "access": {"handlers": ["json_access"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"handlers": ["json"], "level": "INFO", "propagate": False},
        },
        "root": {"level": "INFO", "handlers": ["json"]},
    }


def _override_handlers(loggers: Dict[str, Dict], handler: str) -> Dict[str, Dict]:
    with_handlers: Dict[str, Dict] = {}
    defaults: Dict[str, Any] = {"level": "INFO"}
    overrides: Dict[str, Any] = {"handlers": [handler], "propagate": False}
    for k, v in loggers.items():
        with_handlers[k] = {**defaults, **(v or {}), **overrides}
    return with_handlers


def configure_logging(app_env: str, loggers: Dict[str, Dict] = None) -> Dict[str, Any]:
    """Return the standard logging config. Pass in a dict with app-specific loggers to
    include them in the output. Uvicorn and access logs are configured by default."""
    if loggers is None:
        loggers = {}

    if app_env != "development":
        base_config = get_prod_config()
        app_handler = "json"
    else:
        base_config = get_dev_config()
        app_handler = "console"

    return {
        **base_config,
        "loggers": {
            **(base_config.get("loggers", {})),
            **_override_handlers(loggers, app_handler),
        },
    }
