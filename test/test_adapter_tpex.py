import copy

import pytest

from src.adapter import tpex
from src.box.exceptions import HolidayWarning
from src.proxy import provider


@pytest.mark.run(order=3)
class TestTpexFetcher:
    SLEEP_SECOND = 5

    def __raise(self, callable, *args, **kwargs):
        try:
            callable(*args, **kwargs)
        except Exception as e:
            return type(e)
        else:
            return None

    def setup(self):
        self.tpex_init_kwargs = {
            "proxy_provider": provider.NoProxyProvier(),
            "enable_fetch_price": False,
            "enable_fetch_institutional_investors": False,
            "enable_fetch_credit_transactions_securities": False,
            "sleep_second": self.SLEEP_SECOND,
        }
        self.obj = tpex.TPEXFetcher(**self.tpex_init_kwargs)

    def test_initialize_arguments(self):
        assert self.obj._sleep_second == self.SLEEP_SECOND

    def test_tpex_base_url(self):
        assert self.obj.TPEX_BASE_URL == "http://www.tpex.org.tw/"

    def test_republic_era_datetime(self):
        year, month, day = self.obj.republic_era_datetime(date="20200101")
        assert year == 109
        assert month == 1
        assert day == 1

    def test_adapter_fetch_price(self):
        obj = copy.deepcopy(self.obj)
        response = self.__raise(obj.adapter_fetch_price, "20061231")
        assert response is None

        obj._enable_fetch_price = True
        response = self.__raise(obj.adapter_fetch_price, "20061231")
        assert response is NotImplementedError

        response = self.__raise(obj.adapter_fetch_price, "20070101")
        assert response is HolidayWarning

        data = obj.adapter_fetch_price("20070102")
        assert data["5483"] == ["5483", "中美晶", "94.90", "95.00", "92.00", "92.30", "4784000", "2193", "445753600"]

        response = self.__raise(obj.adapter_fetch_price, "20070701")
        assert response is HolidayWarning

        data = obj.adapter_fetch_price("20070702")
        assert data["5483"] == ["5483", "中美晶", "206.50", "216.50", "206.50", "214.50", "6359000", "3611", "1347834500"]

    def test_adapter_fetch_institutional_investors(self):
        obj = copy.deepcopy(self.obj)
        response = self.__raise(obj.adapter_fetch_institutional_investors, "20070422")
        assert response is None

        obj._enable_fetch_institutional_investors = True
        response = self.__raise(obj.adapter_fetch_institutional_investors, "20070422")
        assert response is NotImplementedError

        data = obj.adapter_fetch_institutional_investors("20070423")
        assert data["5483"] == [
            "6000",
            "1000",
            "5000",
            "300000",
            "125000",
            "175000",
            "318000",
            "30000",
            "288000",
            "468000",
        ]

        response = self.__raise(obj.adapter_fetch_institutional_investors, "20070429")
        assert response is HolidayWarning

        data = obj.adapter_fetch_institutional_investors("20141201")
        assert data["1565"] == ["178491", "133491", "45000", "0", "28000", "-28000", "21000", "7000", "14000", "31000"]

        response = self.__raise(obj.adapter_fetch_institutional_investors, "20141207")
        assert response is HolidayWarning

        data = obj.adapter_fetch_institutional_investors("20180115")
        assert data["5274"] == ["6000", "23000", "-17000", "40000", "16000", "24000", "1000", "4000", "-3000", "4000"]

    def test_adapter_fetch_credit_transactions_securities(self):
        obj = copy.deepcopy(self.obj)
        response = self.__raise(obj.adapter_fetch_credit_transactions_securities, "20030731")
        assert response is None

        obj._enable_fetch_credit_transactions_securities = True
        response = self.__raise(obj.adapter_fetch_credit_transactions_securities, "20030731")
        assert response is NotImplementedError

        response = self.__raise(obj.adapter_fetch_credit_transactions_securities, "20030801")
        assert response is NotImplementedError

        response = self.__raise(obj.adapter_fetch_credit_transactions_securities, "20070101")
        assert response is HolidayWarning

        data = obj.adapter_fetch_credit_transactions_securities("20070102")
        assert data["5483"] == ["1845", "2328", "0", "32360", "45890", "3", "202", "1", "1752", "45890", "", "113"]
