from functools import wraps
from time import sleep

import requests

from .exceptions import HolidayWarning


def monitor(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        arguments = [str(arg) for arg in args[1:]] + ['f{k}={v}' for k, v in kwargs.items()]
        arguments = ', '.join(arguments)
        print(f'{func.__qualname__}({arguments})')

        for i in range(3):
            try:
                return func(*args, **kwargs)
            except HolidayWarning as e:
                sleep(2)
                print(e)
                return
            except (requests.exceptions.ConnectionError, ConnectionError) as e:
                print(e)
                sleep(30)
    return wrapper
