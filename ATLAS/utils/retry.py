"""
Retry decorator with exponential backoff for ATLAS agents.
Used on all external API calls (Anthropic, Reddit, Vercel, Resend).
"""

import time
import logging
import functools
from typing import Callable, Type, Tuple

logger = logging.getLogger('atlas.retry')


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Callable = None,
):
    """
    Decorator that retries a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds (doubles each retry)
        max_delay: Maximum delay cap
        exceptions: Tuple of exception types to catch
        on_retry: Optional callback(attempt, exception, delay) called before each retry
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(
                            f"RETRY EXHAUSTED: {func.__name__} failed after "
                            f"{max_retries + 1} attempts. Last error: {e}"
                        )
                        raise

                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(
                        f"RETRY {attempt + 1}/{max_retries}: {func.__name__} "
                        f"failed with {type(e).__name__}: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    if on_retry:
                        on_retry(attempt, e, delay)

                    time.sleep(delay)

            raise last_exception

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            import asyncio
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(
                            f"RETRY EXHAUSTED: {func.__name__} failed after "
                            f"{max_retries + 1} attempts. Last error: {e}"
                        )
                        raise

                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(
                        f"RETRY {attempt + 1}/{max_retries}: {func.__name__} "
                        f"failed with {type(e).__name__}: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    if on_retry:
                        on_retry(attempt, e, delay)

                    await asyncio.sleep(delay)

            raise last_exception

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    return decorator
