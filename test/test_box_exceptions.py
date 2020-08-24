from stock.box.exceptions import HolidayWarning


def test_exception_str():
    assert str(HolidayWarning('ERROR_DATE')) == 'ERROR_DATE is holiday'
