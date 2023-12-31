from typing import Optional

from pydantic import BaseModel


class KafkaMessage(BaseModel):
    topic: str
    message: str


class RedisValueDTO(BaseModel):
    key: str
    value: Optional[str]


class RMQMessageDTO(BaseModel):
    exchange_name: str
    routing_key: str
    message: str


class TiqBody(BaseModel):
    value: int
