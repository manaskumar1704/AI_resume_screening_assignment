from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import latency


def setup_metrics(app: FastAPI) -> None:
    """Setup Prometheus metrics collection."""

    instrumentator = Instrumentator(
        should_group_untemplated=True,
        excluded_handlers=[
            "/health",
            "/health/live",
            "/health/ready",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ],
    )

    instrumentator.add(latency()).instrument(app).expose(app, endpoint="/metrics")


# This function is called from main.py to setup metrics
