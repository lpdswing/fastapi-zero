import functools
import logging
import os
import sys

from asgi_correlation_id import correlation_id
from loguru import logger

from src.config import settings
from src.middlewares import global_userid

__all__ = ["log", "logger_wraps", "init_logger"]


def correlation_id_filter(record):
    record["correlation_id"] = correlation_id.get()
    record["user_id"] = global_userid.get()
    return record


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def init_logger():
    logger_names = ("uvicorn.asgi", "uvicorn.access", "uvicorn")
    logging.getLogger().handlers = [InterceptHandler()]
    for logger_name in logger_names:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]


log = logger
log.remove()
fmt = "[<red>{correlation_id}</red>][<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>][uid: {user_id}][<level>{level: <8}</level>][pid: {process}]| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
log.add(sys.stderr, format=fmt, level=logging.DEBUG, filter=correlation_id_filter)
log.add(
    os.path.join(settings.LOG_DIR, "access.{time:YYYY-MM-DD}.log"),
    format=fmt,
    level=logging.INFO,
    filter=correlation_id_filter,
    rotation=settings.ROTATION,
    retention=settings.RETENTION,
)
log.add(
    os.path.join(settings.LOG_DIR, "error.{time:YYYY-MM-DD}.log"),
    format=fmt,
    level=logging.ERROR,
    filter=correlation_id_filter,
    rotation=settings.ROTATION,
    retention=settings.RETENTION,
)


# log wrappers
def logger_wraps(*, entry=True, exit=True, level="DEBUG"):
    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = log.opt(depth=1)
            if entry:
                logger_.log(
                    level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs
                )
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper
