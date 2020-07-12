import itertools


class BaseFetcher:
    HEADERS = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0',
        'Accept-Encoding': 'gzip, deflate, compress'
    }

    def __init__(self):
        pass

    @property
    def columns(self):
        return [
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

    def republic_era_datetime(self, date):
        year = int(date[0:4]) - 1911
        month = date[4:6]
        day = date[6:8]
        return year, month, day

    def clean(self, value):
        if type(value) is str:
            value = None if '--' in value else value.replace(',', '').strip()
        return value

    def combine(self, date: str, price: dict, institutional_investors: dict) -> list:
        results = []
        for id in price.keys():
            volume = [date] + price[id] + institutional_investors.get(id, [])
            results += [
                dict(itertools.zip_longest(self.columns, volume, fillvalue='0'))
            ]
        return results
