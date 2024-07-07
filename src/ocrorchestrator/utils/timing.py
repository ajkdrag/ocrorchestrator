import asyncio
import time
from functools import wraps
from typing import Any, Callable

import structlog

logger = structlog.get_logger()


def log_execution_time(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        log_time(func, start_time, end_time, args)
        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        log_time(func, start_time, end_time, args)
        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def log_time(func, start_time, end_time, args):
    execution_time = end_time - start_time

    # Get the class name if the function is a method
    class_name = (
        args[0].__class__.__name__ if args and hasattr(args[0], "__class__") else None
    )

    log_data = {
        "function": func.__name__,
        "execution_time_millis": execution_time * 1000,
        "module": func.__module__,
    }
    if class_name:
        log_data["class"] = class_name

    logger.info("--- Function execution time ---", **log_data)
