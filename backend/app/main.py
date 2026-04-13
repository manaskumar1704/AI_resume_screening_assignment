import structlog
from contextlib import asynccontextmanager
from contextvars import ContextVar
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request
from uuid import uuid4

from app.config import settings
from app.api.routes import evaluations
from app.api.routes import health
from app.api.routes.metrics import setup_metrics

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# Correlation ID context variable
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = structlog.get_logger()
    logger.info(
        "starting_api", provider=settings.LLM_PROVIDER, model=settings.LLM_MODEL
    )
    logger.info(
        "database_configured",
        host=settings.DATABASE_URL.split("@")[1]
        if "@" in settings.DATABASE_URL
        else settings.DATABASE_URL,
    )
    logger.info(
        "redis_configured",
        host=settings.REDIS_URL.split("@")[1]
        if "@" in settings.REDIS_URL
        else settings.REDIS_URL,
    )
    yield
    structlog.get_logger().info("shutting_down_api")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Resume Screening Service",
        description="AI-powered resume screening against job descriptions",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Setup Prometheus metrics
    setup_metrics(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_correlation_id(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        correlation_id_var.set(request_id)

        logger = structlog.get_logger().bind(correlation_id=request_id)

        # Log request start
        logger.info("request_started", method=request.method, path=request.url.path)

        try:
            response = await call_next(request)
            logger.info("request_completed", status_code=response.status_code)
            return response
        except Exception as e:
            logger.error("request_failed", error=str(e))
            raise

    # Include routers
    app.include_router(evaluations.router, prefix="/api/v1", tags=["evaluations"])
    app.include_router(health.router, tags=["health"])

    # Remove old /health endpoint - replaced by health router
    # Old: @app.get("/health") async def health_check(): return JSONResponse({"status": "ok"})

    return app


app = create_app()
