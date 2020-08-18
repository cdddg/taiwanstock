from stock.foundation import twse
from stock.box.exceptions import HolidayWarning

import time


class TestTwseFetcher:
    SLEEP_SECOND = 3

    def __raise(self, callable, *args, **kwargs):
        try:
            callable(*args, **kwargs)
        except Exception as e:
            return type(e)
        else:
            return None

    def setup(self):
        self.obj = twse.TWSEFetcher(sleep_second=self.SLEEP_SECOND)

    def test_initialize_arguments(self):
        assert self.obj.sleep_second == self.SLEEP_SECOND

    def test_tpex_base_url(self):
        assert self.obj.TWSE_BASE_URL == 'http://www.twse.com.tw/'

    def test_adapter(self):
        return
        assert self.__raise(self.obj._adapter, '20120430') is NotImplementedError
        assert self.__raise(self.obj._adapter, '20120501') is HolidayWarning

    def test_price(self):
        time.sleep(self.SLEEP_SECOND)
        data = self.obj._price_20040211_now('20200102')
        assert data['2330'] == [
            '2330', '台積電', '332.50', '339.00', '332.50', '339.00', '+8.00', '2.42', '33282120', '17160', '11224165450'
        ]

    def test_institutional_investors(self):
        time.sleep(self.SLEEP_SECOND)
        data = self.obj._institutional_investors_20120502_now('20200102')
        assert data['2330'] == [
            '13041781', '17798488', '-4756707', '20000', '199000', '-179000', '692000', '709000', '-17000', '-4952707'
        ]

