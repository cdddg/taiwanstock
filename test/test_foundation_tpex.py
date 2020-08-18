from stock.foundation import tpex
from stock.box.exceptions import HolidayWarning

import time


class TestTpexFetcher:
    SLEEP_SECOND = 3

    def __raise(self, callable, *args, **kwargs):
        try:
            callable(*args, **kwargs)
        except Exception as e:
            return type(e)
        else:
            return None

    def setup(self):
        self.obj = tpex.TPEXFetcher(sleep_second=self.SLEEP_SECOND)

    def test_initialize_arguments(self):
        assert self.obj.sleep_second == self.SLEEP_SECOND

    def test_tpex_base_url(self):
        assert self.obj.TPEX_BASE_URL == 'http://www.tpex.org.tw/'

    def test_republic_era_datetime(self):
        year, month, day = self.obj.republic_era_datetime(date='20200101')
        assert year == 109
        assert month == 1
        assert day == 1

    def test_adapter(self):
        assert self.__raise(self.obj._adapter, '20061231') is NotImplementedError
        assert self.__raise(self.obj._adapter, '20070101') is HolidayWarning

    def test_fetch_price(self):
        return
        time.sleep(self.SLEEP_SECOND)
        data = self.obj._price_20070101_20070630('20070105')
        assert data['4303'] == [
            '4303', '信立', '2.95', '2.95', '2.72', '2.72', '-0.20', '-6.85', '847000', '134', '2365010'
        ]
        assert data['70281'] == [
            '70281', '中信T6', '3.90', '4.25', '3.90', '3.90', '-2.40', '-38.1', '268000', '55', '1053150'
        ]

        time.sleep(self.SLEEP_SECOND)
        data = self.obj._price_20070701_now('20070702')
        assert data['4303'] == [
            '4303', '信立', '2.57', '2.57', '2.57', '2.57', '+0.16', '6.64', '2013000', '178', '5173410'
        ]

        time.sleep(self.SLEEP_SECOND)
        data = self.obj._price_20070701_now('20200102')
        assert data['4303'] == [
            '5274', '信驊', '968.00', '984.00', '959.00', '970.00', '+11.00', '1.15', '205000', '202', '198885000'
        ]

    def test_fetch_institutional_investors(self):
        time.sleep(self.SLEEP_SECOND)
        data = self.obj._institutional_investors_20050421_20141130('20070426')
        assert data['3227'] == [
            '970000', '779000', '191000', '3000', '54000', '-51000', '9000', '147000', '-138000', '2000'
        ]

        time.sleep(self.SLEEP_SECOND)
        data = self.obj._institutional_investors_20141201_now('20200102')
        assert data['3227'] == [
            '370000', '187000', '183000', '0', '0', '0', '205000', '293000', '-88000', '95000'
        ]
