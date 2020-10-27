import pytest

from src.box.exceptions import HolidayWarning


@pytest.mark.run(order=1)
def test_exception_str():
    assert str(HolidayWarning("ERROR_DATE")) == "ERROR_DATE is holiday"
