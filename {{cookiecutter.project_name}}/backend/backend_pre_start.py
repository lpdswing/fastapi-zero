import asyncio
import logging

import aio_pika
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from src.config import settings
from src.lib.logger import log

pg_uri = str(settings.SQLALCHEMY_DATABASE_URI).replace("+asyncpg", "")
engine = create_engine(pg_uri, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(log, logging.INFO),
    after=after_log(log, logging.WARN),
)
def init() -> None:
    try:
        db = SessionLocal()
        # Try to create session to check if DB is awake
        db.execute(text("SELECT 1"))
    except Exception as e:
        log.error(e)
        raise e


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(log, logging.INFO),
    after=after_log(log, logging.WARN),
)
async def check_rabbitmq() -> None:
    try:
        conn = await aio_pika.connect_robust(str(settings.RABBIT_URL))
        await conn.close()
    except Exception as e:
        log.error(e)
        raise e


def main() -> None:
    log.info("Initializing service")
    init()
    asyncio.run(check_rabbitmq())
    log.info("Service finished initializing")


if __name__ == "__main__":
    main()
