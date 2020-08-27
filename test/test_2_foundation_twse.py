import copy
import time

from stock.box.exceptions import HolidayWarning
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

    def test_adapter_fetch_price(self):
        obj = copy.deepcopy(self.obj)
        response = self.__raise(obj.adapter_fetch_price, '20040210')
        assert response is None

        obj._enable_fetch_price = True
        response = self.__raise(obj.adapter_fetch_price, '20040210')
        assert response is NotImplementedError

        data = obj.adapter_fetch_price('20040211')
        assert data['2454'] == ['2454', '聯發科', '359.00', '362.00', '354.00', '357.00', '3274043', '1873', '1170606331']

    def test_adapter_fetch_institutional_investors(self):
        obj = copy.deepcopy(self.obj)
        response = self.__raise(obj.adapter_fetch_institutional_investors, '20120501')
        assert response is None

        obj._enable_fetch_institutional_investors = True
        response = self.__raise(obj.adapter_fetch_institutional_investors, '20120501')
        assert response is NotImplementedError

        data = obj.adapter_fetch_institutional_investors('20120502')
        assert data['3008'] == ['979000', '997112', '-18112', '82000', '414000', '-332000', '77000', '44000', '33000', '-317112']

        response = self.__raise(obj.adapter_fetch_institutional_investors, '20120505')
        assert response is HolidayWarning

        data = obj.adapter_fetch_institutional_investors('20141201')
        assert data['3008'] == ['180000', '273695', '-93695', '27000', '2000', '25000', '224000', '87000', '137000', '68305']

        data = obj.adapter_fetch_institutional_investors('20171218')
        assert data['3008'] == ['553051', '366488', '186563', '3000', '34600', '-31600', '36000', '11000', '25000', '179963']

    def test_adapter_fetch_credit_transactions_securities(self):
        obj = copy.deepcopy(self.obj)
        response = self.__raise(obj.adapter_fetch_credit_transactions_securities, '20001231')
        assert response is None

        obj._enable_fetch_credit_transactions_securities = True
        response = self.__raise(obj.adapter_fetch_credit_transactions_securities, '20001231')
        assert response is NotImplementedError

        response = self.__raise(obj.adapter_fetch_credit_transactions_securities, '20010101')
        assert response is HolidayWarning

        data = obj.adapter_fetch_credit_transactions_securities('20010102')
        assert data['2317'] == ['1692', '1447', '12', '16481', '363225', '1177', '1274', '4', '7066', '363225', '2262', '']
