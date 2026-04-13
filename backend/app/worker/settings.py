import logging
from arq.connections import RedisSettings

from app.config import settings


logger = logging.getLogger(__name__)


class WorkerSettings:
    """ARQ worker settings for resume screening."""

    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    functions = ["app.worker.tasks.screen_resume"]
    max_jobs = 10
    job_timeout = 300
    keep_result = 3600

    @staticmethod
    async def on_startup(ctx):
        logger.info("ARQ Worker starting up")

    @staticmethod
    async def on_shutdown(ctx):
        logger.info("ARQ Worker shutting down")


worker_settings = WorkerSettings
