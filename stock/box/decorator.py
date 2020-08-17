from functools import wraps
from time import sleep

import requests

from .exceptions import HolidayWarning

DEFAULT_RUN_TIMES = 3


def monitor(factor_or_func: int or object = None):
    def _inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(func.__qualname__ + '()')

            if 'factor_or_func' not in locals() \
                    or callable(factor_or_func) \
                    or factor_or_func is None:
                factor = DEFAULT_RUN_TIMES
            else:
                factor = factor_or_func
            for i in range(factor):
                try:
                    return func(*args, **kwargs)
                except HolidayWarning as e:
                    sleep(2)
                    print(e)
                    return
                except (requests.exceptions.ConnectionError, ConnectionError) as e:
                    print(e)
                    sleep(30)
                except NotImplementedError:
                    raise
        return wrapper
    return _inner(factor_or_func) if callable(factor_or_func) else _inner
