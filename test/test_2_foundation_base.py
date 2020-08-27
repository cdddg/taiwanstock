from stock.foundation import base


class TestBaseFetcher:
    def setup(self):
        self.obj = base.BaseFetcher()

    def test_headers(self):
        assert self.obj.HEADERS == {
            'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0',
            'Accept-Encoding': 'gzip, deflate, compress'
        }

    def test_columns(self):
        assert self.obj.price_columns == [
            'date',
            'sid',
            'name',
            'open',
            'high',
            'low',
            'close',
            'capacity',
            'transaction',
            'turnover',
        ]
        assert self.obj.institutional_investors_columns == [
            'foreign_dealers_buy',
            'foreign_dealers_sell',
            'foreign_dealers_total',
            'investment_trust_buy',
            'investment_trust_sell',
            'investment_trust_total',
            'dealer_buy',
            'dealer_sell',
            'dealer_total',
            'institutional_investors_total',
        ]
        assert self.obj.credit_transactions_securities_columns == [
            'margin_purchase',
            'margin_sales',
            'margin_cash_redemption',
            'margin_today_balance',
            'margin_quota',
            'short_covering',
            'short_sale',
            'short_stock_redemption',
            'short_today_balance',
            'short_quota',
            'offsetting_margin_short',
            'note',
        ]

    def test_clean(self):
        assert self.obj.clean('-') == '-'
        assert self.obj.clean('--') is None
        assert self.obj.clean('---') is None
        assert self.obj.clean('----') is None
        assert self.obj.clean('1,000') == '1000'
        assert self.obj.clean('1,000,000') == '1000000'

    def test_combine(self):
        return NotImplemented
