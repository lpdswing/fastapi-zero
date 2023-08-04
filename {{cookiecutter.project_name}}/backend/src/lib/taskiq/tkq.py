import taskiq_fastapi
from taskiq import InMemoryBroker
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from src.config import settings

result_backend = RedisAsyncResultBackend(
    redis_url=str(settings.REDIS_URL),
)
broker = AioPikaBroker(
    str(settings.RABBIT_URL),
).with_result_backend(result_backend)

if settings.ENVIRONMENT.is_testing:
    broker = InMemoryBroker()

taskiq_fastapi.init(
    broker,
    "src.main:app",
)
