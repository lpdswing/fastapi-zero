from src.lib.taskiq.tkq import broker


@broker.task
async def add_one(value: int) -> int:
    return value + 1
