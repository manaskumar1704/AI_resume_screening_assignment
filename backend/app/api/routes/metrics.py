from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import (
    Counter,
    Histogram,
    Info,
)


def setup_metrics(app: FastAPI) -> None:
    """Setup Prometheus metrics collection."""

    instrumentator = Instrumentator(
        should_group_responses=False,
        should_ignore_untemplated=True,
        excludes=[
            "/health",
            "/health/live",
            "/health/ready",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ],
    )

    @instrumentator.summary("custom_req_size", "Request size in bytes")
    def req_size():
        return 0  # Placeholder for custom metrics

    instrumentator.instrument(app).expose(app, endpoint="/metrics")


# This function is called from main.py to setup metrics
