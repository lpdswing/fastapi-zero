import asyncio

from aiokafka import AIOKafkaConsumer, TopicPartition


async def consume():
    consumer = AIOKafkaConsumer(
        "gogo",
        bootstrap_servers="kafka:9092",
        # auto_offset_reset='earliest'
    )
    # Get cluster layout and join group `my-group`
    await consumer.start()
    try:
        # Consume messages
        partitions = consumer.partitions_for_topic("gogo")
        print(partitions)
        partition = partitions.pop()
        # await consumer.seek_to_beginning(TopicPartition('gogo', partition))
        print(partition)
        consumer.seek(TopicPartition("gogo", partition), 0)

        # while True:
        data = await consumer.getmany(TopicPartition("gogo", partition), timeout_ms=1000)
        for messages in data.values():
            for message in messages:
                topic = message.topic
                partition = message.partition
                # Process message
                print(message.offset, message.key, message.value, partition, topic)
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()


asyncio.run(consume())
