from fastapi import FastAPI
from redis.asyncio import ConnectionPool

from src.config import settings


def init_redis(app: FastAPI) -> None:  # pragma: no cover
    """
    Creates connection pool for redis.

    :param app: current fastapi application.
    """
    app.state.redis_pool = ConnectionPool.from_url(
        str(settings.REDIS_URL),
    )


async def shutdown_redis(app: FastAPI) -> None:  # pragma: no cover
    """
    Closes redis connection pool.

    :param app: current FastAPI app.
    """
    await app.state.redis_pool.disconnect()
