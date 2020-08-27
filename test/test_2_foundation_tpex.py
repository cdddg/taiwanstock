import time

from stock.foundation import tpex


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
        self.tpex_init_kwargs = {
            'enable_fetch_price': False,
            'enable_fetch_institutional_investors': False,
            'enable_fetch_credit_transactions_securities': False,
            'sleep_second': self.SLEEP_SECOND
        }
        self.obj = tpex.TPEXFetcher(**self.tpex_init_kwargs)

    def test_initialize_arguments(self):
        assert self.obj._sleep_second == self.SLEEP_SECOND

    def test_tpex_base_url(self):
        assert self.obj.TPEX_BASE_URL == 'http://www.tpex.org.tw/'

    def test_republic_era_datetime(self):
        year, month, day = self.obj.republic_era_datetime(date='20200101')
        assert year == 109
        assert month == 1
        assert day == 1

    def test_adapter(self):
        params = self.tpex_init_kwargs.copy()
        params['enable_fetch_price'] = True
        object = tpex.TPEXFetcher(**params)
        assert self.__raise(object.adapter, '20061231') is NotImplementedError

        params = self.tpex_init_kwargs.copy()
        params['enable_fetch_institutional_investors'] = True
        object = tpex.TPEXFetcher(**params)
        assert self.__raise(object.adapter, '20050420') is NotImplementedError

    def test_fetch_price(self):
        time.sleep(self.SLEEP_SECOND)
        data = self.obj._price_20070101_20070630('20070105')
        assert data['4303'] == [
            '4303', '信立', '2.95', '2.95', '2.72', '2.72', '847000', '134', '2365010'
        ]

        time.sleep(self.SLEEP_SECOND)
        data = self.obj._price_20070701_now('20070702')
        assert data['4303'] == [
            '4303', '信立', '2.57', '2.57', '2.57', '2.57', '2013000', '178', '5173410'
        ]

        time.sleep(self.SLEEP_SECOND)
        data = self.obj._price_20070701_now('20200102')
        assert data['5274'] == [
            '5274', '信驊', '968.00', '984.00', '959.00', '970.00', '205000', '202', '198885000'
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

    def test_fetch_credit_transactions_securities(self):
        response = self.__raise(self.obj._credit_transactions_securities_20030801_20061231, '20061231')
        assert response is NotImplementedError

        time.sleep(self.SLEEP_SECOND)
        data = self.obj._credit_transactions_securities_20070101_now('20200102')
        assert data['3227'] == [
            '778', '540', '0', '13353', '34301', '60', '40', '0', '1627', '34301', '2', ''
        ]
