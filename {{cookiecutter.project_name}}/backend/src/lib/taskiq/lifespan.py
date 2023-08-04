from src.lib.taskiq.tkq import broker


async def init_taskiq():
    if not broker.is_worker_process:
        await broker.startup()


async def shutdown_taskiq():
    if not broker.is_worker_process:
        await broker.shutdown()
