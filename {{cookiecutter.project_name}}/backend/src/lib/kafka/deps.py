from aiokafka import AIOKafkaProducer
from fastapi import Request
from taskiq import TaskiqDepends


def get_kafka_producer(request: Request = TaskiqDepends()) -> AIOKafkaProducer:
    return request.app.state.kafka_producer
