from functools import wraps
from time import sleep

import requests

from .exceptions import HolidayWarning

DEFAULT_RUN_TIMES = 3


def monitor(factor_or_func: int or object = None):
    def _decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            params = ', '.join([str(a) for a in args[1:]] + [f'{k}={v}' for k, v in kwargs])
            print(func.__qualname__ + f'({params})')

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
                    print(f'  --{type(e).__name__}: "{e}"')
                    sleep(30)
                except (Exception, NotImplementedError):
                    raise
        return wrapper
    return _decorator(factor_or_func) if callable(factor_or_func) else _decorator
