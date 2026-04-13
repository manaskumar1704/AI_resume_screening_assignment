from arq import WorkerSettings

from app.config import settings


class WorkerSettings(WorkerSettings):
    redis_url = settings.REDIS_URL
    functions = ["app.worker.tasks.screen_resume"]

    @classmethod
    def getRedisSettings(cls):
        from arq.connections import RedisSettings

        return RedisSettings.from_dsn(cls.redis_url)


worker_settings = WorkerSettings
