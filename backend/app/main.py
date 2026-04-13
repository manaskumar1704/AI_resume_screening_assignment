import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request
from uuid import uuid4

from app.config import settings
from app.api.routes import evaluations

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        f"Starting API with settings: LLM_PROVIDER={settings.LLM_PROVIDER}, LLM_MODEL={settings.LLM_MODEL}"
    )
    logger.info(
        f"DATABASE_URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}"
    )
    logger.info(
        f"REDIS_URL: {settings.REDIS_URL.split('@')[1] if '@' in settings.REDIS_URL else settings.REDIS_URL}"
    )
    yield
    logger.info("Shutting down API")


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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    app.include_router(evaluations.router, prefix="/api/v1", tags=["evaluations"])

    @app.get("/health")
    async def health_check():
        return JSONResponse({"status": "ok"})

    return app


app = create_app()
