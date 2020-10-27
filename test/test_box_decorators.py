import pytest


@pytest.mark.run(order=1)
def test_decorator_monitor():
    return NotImplemented
    # from src.box.decorators import monitor
    # @monitor
    # def _inner1(*args, **kwargs):
    #     raise ConnectionError

    # try:
    #     _inner1()
    # except Exception as e:
    #     print(e)
