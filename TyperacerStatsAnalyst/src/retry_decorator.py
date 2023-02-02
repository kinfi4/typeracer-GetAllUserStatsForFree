import random
from time import sleep
from typing import Callable
from functools import wraps


def exponential_backoff(retry_count: int) -> None:
    seconds_to_sleep = 2 ** retry_count + random.uniform(0, 2)
    sleep(seconds_to_sleep)


def retry(
    max_retries: int = 4,
    backoff_function: Callable = exponential_backoff,
    exception_to_raise: Exception = None,
    context: str = "Retrying function"
):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            retries_count = 0

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if retries_count > max_retries:
                        if exception_to_raise is None:
                            raise
                        else:
                            raise exception_to_raise

                    retries_count += 1
                    print(f"{context}, with retries count: {retries_count}")
                    backoff_function(retries_count)

        return inner

    return decorator
