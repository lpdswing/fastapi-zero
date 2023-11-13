from aio_pika import Channel, Message
from aio_pika.pool import Pool
from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from src.lib.kafka.deps import get_kafka_producer
from src.lib.rabbitmq.deps import get_rmq_channel_pool
from src.lib.redis.deps import get_redis
from src.lib.taskiq.tasks import add_one
from src.utils.schemas import KafkaMessage, RedisValueDTO, RMQMessageDTO, TiqBody

router = APIRouter()


@router.post("/kafka")
async def send_kafka_message(
    kafka_message: KafkaMessage,
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
) -> None:
    await producer.send(
        topic=kafka_message.topic,
        value=kafka_message.message.encode(),
    )


@router.put("/redis")
async def set_redis_value(redis_value: RedisValueDTO, redis: Redis = Depends(get_redis)) -> None:
    if redis_value.value is not None:
        await redis.set(name=redis_value.key, value=redis_value.value)


@router.get("/redis", response_model=RedisValueDTO)
async def get_redis_value(key: str, redis: Redis = Depends(get_redis)) -> RedisValueDTO:
    value = await redis.get(key)
    return RedisValueDTO(key=key, value=value)


@router.post("/rabbitmq")
async def send_rmq_msg(
    message: RMQMessageDTO,
    pool: Pool[Channel] = Depends(get_rmq_channel_pool),
) -> None:
    """
    Posts a message in a rabbitMQ's exchange.

    :param message: message to publish to rabbitmq.
    :param pool: rabbitmq channel pool
    """
    async with pool.acquire() as conn:
        exchange = await conn.declare_exchange(
            name=message.exchange_name,
            auto_delete=True,
        )
        await exchange.publish(
            message=Message(
                body=message.message.encode("utf-8"),
                content_encoding="utf-8",
                content_type="text/plain",
            ),
            routing_key=message.routing_key,
        )


@router.post("/taskiq")
async def test_taskiq(payload: TiqBody) -> int | None:
    task = await add_one.kiq(payload.value)
    res = await task.wait_result(timeout=2)
    return res.return_value
