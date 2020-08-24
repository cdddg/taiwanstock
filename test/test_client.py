import json
import os

from stock import client


class TestStockClient:
    PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testdata')

    def setup(self):
        self.client = client.TaiwanStockClient(
            version='test.0.0.1',
            enable_fetch_institutional_investors=True,
            enable_fetch_credit_transactions_securities=False
        )

    def test_version(self):
        assert self.client._version == 'test.0.0.1'

    def test_fetch_rawdata(self):
        with open(os.path.join(self.PATH, '20200102.json')) as f:
            testdata = json.load(f)
            for row in self.client.fetch(2020, 1, 2):
                sid = row['sid']
                assert testdata.pop(sid) == row
            assert len(testdata) == 0

    # def test_fetch_sql(self):
        # NotImplementedError
