import json
import os
import time

import pytest

from src import client


@pytest.mark.run(order=4)
class TestStockClient:
    PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testdata")

    def __assert(self, rawdata, testdata):
        if rawdata is None:
            return
        for row in rawdata:
            sid = row["sid"]
            assert testdata.pop(sid) == row
        assert len(testdata) == 0

    def test_version(self):
        assert client.TaiwanStockClient(version="test0.0.1", sleep_second=5)._version == "test0.0.1"

    def test_fetch_rawdata(self):
        print("")
        # 每日盤後行情、三大法人買賣超、融資融券餘額
        date = [
            (2018, 1, 15),
            (2017, 12, 18),
            (2014, 12, 1),
            (2012, 5, 2),
        ]
        object = client.TaiwanStockClient(
            enable_fetch_institutional_investors=True, enable_fetch_credit_transactions_securities=True
        )
        for year, month, day in date:
            with open(os.path.join(self.PATH, f"{year}{month:0>2}{day:0>2}.json")) as f:
                time.sleep(5)
                self.__assert(object.fetch(year, month, day), json.load(f))

        # 每日盤後行情、融資融券餘額
        date = [
            (2007, 7, 1),
            (2007, 7, 2),
            (2007, 1, 1),
            (2007, 1, 2),
        ]
        object = client.TaiwanStockClient(
            enable_fetch_institutional_investors=False, enable_fetch_credit_transactions_securities=True
        )
        for year, month, day in date:
            time.sleep(5)
            rawdata = object.fetch(year, month, day)
            if rawdata:
                with open(os.path.join(self.PATH, f"{year}{month:0>2}{day:0>2}.json")) as f:
                    testdata = json.load(f)
                self.__assert(rawdata, testdata)

    # def test_fetch_sql(self):
    # NotImplementedError
