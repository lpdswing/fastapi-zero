from typing import AsyncGenerator

from fastapi import Depends
from starlette.requests import Request
from taskiq import TaskiqDepends
from redis.asyncio import ConnectionPool, Redis


async def get_redis_pool(
        request: Request = TaskiqDepends(),
) -> AsyncGenerator[Redis, None]:  # pragma: no cover
    """
    Returns connection pool.

    You can use it like this:

    >>> from redis.asyncio import ConnectionPool, Redis
    >>>
    >>> async def handler(redis_pool: ConnectionPool = Depends(get_redis_pool)):
    >>>     async with Redis(connection_pool=redis_pool) as redis:
    >>>         await redis.get('key')

    I use pools, so you don't acquire connection till the end of the handler.

    :param request: current request.
    :returns:  redis connection pool.
    """
    return request.app.state.redis_pool


async def get_redis(pool: ConnectionPool = Depends(get_redis_pool)):
    redis = Redis(connection_pool=pool)
    try:
        yield redis
    finally:
        await redis.close()
