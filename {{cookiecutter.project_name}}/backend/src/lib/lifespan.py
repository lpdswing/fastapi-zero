from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config import settings
from src.lib.logger import init_logger
from src.lib.kafka.lifespan import init_kafka, shutdown_kafka
from src.lib.redis.lifespan import init_redis, shutdown_redis
from src.lib.rabbitmq.lifespan import init_rabbit, shutdown_rabbit
from src.lib.taskiq.lifespan import init_taskiq, shutdown_taskiq


def _startup_db(app: FastAPI) -> None:  # pragma: no cover
    """
    Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    :param app: fastAPI application.
    """
    engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI),
                                 # echo=settings.ENVIRONMENT.is_debug,
                                 echo=False
                                 )
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory


async def _shutdown_db(app: FastAPI) -> None:
    await app.state.db_engine.dispose()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    init_logger()

    # Startup
    await init_taskiq()
    _startup_db(app)
    await init_kafka(app)
    init_redis(app)
    init_rabbit(app)
    yield
    # Shutdown
    await shutdown_taskiq()
    await _shutdown_db(app)
    await shutdown_kafka(app)
    await shutdown_redis(app)
    await shutdown_rabbit(app)


