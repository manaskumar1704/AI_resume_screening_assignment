from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from sqlalchemy import text
import structlog

from app.config import settings

router = APIRouter(tags=["health"])
logger = structlog.get_logger()


@router.get("/health/live")
async def liveness():
    """Liveness probe - returns 200 if process is running."""
    return JSONResponse({"status": "alive"})


@router.get("/health/ready")
async def readiness(response: Response):
    """Readiness probe - returns 200 if DB and Redis are reachable."""
    checks = {"database": False, "redis": False}

    # Check database
    try:
        from app.database import engine

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        logger.error("health_check_db_failed", error=str(e))

    # Check Redis
    try:
        from redis.asyncio import Redis

        redis = Redis.from_url(settings.REDIS_URL)
        await redis.ping()
        await redis.aclose()
        checks["redis"] = True
    except Exception as e:
        logger.error("health_check_redis_failed", error=str(e))

    all_ok = checks["database"] and checks["redis"]

    if all_ok:
        return JSONResponse({"status": "ready", **checks})
    else:
        response.status_code = 503
        return JSONResponse({"status": "not_ready", **checks}, status_code=503)
