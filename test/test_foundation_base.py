from stock.foundation import base


class TestBaseFetcher:
    def setup(self):
        self.obj = base.BaseFetcher()

    def test_headers(self):
        assert self.obj.columns == [
            'date',
            'sid',
            'name',
            'open',
            'high',
            'low',
            'close',
            'amplitude',
            'amplitude_ratio',
            'capacity',
            'transaction',
            'turnover',
            'foreign_dealers_buy',
            'foreign_dealers_sell',
            'foreign_dealers_total',
            'investment_trust_buy',
            'investment_trust_sell',
            'investment_trust_total',
            'dealer_buy',
            'dealer_sell',
            'dealer_total',
            'institutional_investors_total'
        ]

    def test_clean(self):
        assert self.obj.clean('-') == '-'
        assert self.obj.clean('--') is None
        assert self.obj.clean('---') is None
        assert self.obj.clean('----') is None
        assert self.obj.clean('1,000') == '1000'
        assert self.obj.clean('1,000,000') == '1000000'

    def test_combine(self):
        NotImplementedError
