import time

from stock.foundation import twse


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
        self.twse_init_kwargs = {
            'enable_fetch_price': False,
            'enable_fetch_institutional_investors': False,
            'enable_fetch_credit_transactions_securities': False,
            'sleep_second': self.SLEEP_SECOND
        }
        self.obj = twse.TWSEFetcher(**self.twse_init_kwargs)

    def test_initialize_arguments(self):
        assert self.obj._sleep_second == self.SLEEP_SECOND

    def test_tpex_base_url(self):
        assert self.obj.TWSE_BASE_URL == 'http://www.twse.com.tw/'

    def test_adapter(self):
        params = self.twse_init_kwargs.copy()
        params['enable_fetch_price'] = True
        object = twse.TWSEFetcher(**params)
        assert self.__raise(object._adapter, '20040210') is NotImplementedError

        params = self.twse_init_kwargs.copy()
        params['enable_fetch_institutional_investors'] = True
        object = twse.TWSEFetcher(**params)
        assert self.__raise(object._adapter, '20120501') is NotImplementedError

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
