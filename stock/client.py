import os
import csv
import json
import datetime
from .box import tpex, twse
from .foundation.decorator import monitor


PATH = os.path.dirname(os.path.abspath(__file__))


class TaiwanStockClient:
    def __init__(self, version):
        self._version = version
        self.tpex = tpex.TPEXFetcher()
        self.twse = twse.TWSEFetcher()

    @monitor
    def fetch(self, year: int, month: int, day: int):
        rawdata = list()
        rawdata += self.twse.fetch(year, month, day)
        rawdata += self.tpex.fetch(year, month, day)
        return rawdata

    def fetch_to_csv(self, year: int, month: int, day: int):

        if not os.path.isdir(f'{PATH}/rawdata'):
            os.mkdir(f'{PATH}/rawdata')

        if not os.path.isfile(f'{PATH}/rawdata/{year}{month:02}{day:02}.csv'):
            rawdata = self.fetch(year, month, day)
            if rawdata is None:
                return

            with open(f'{PATH}/rawdata/{year}{month:02}{day:02}.csv', 'w', encoding='utf8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=rawdata[0].keys())
                writer.writeheader()
                writer.writerows(rawdata)

    def get_holidays(self):
        with open(f'{PATH}/foundation/holidays.json', 'w+') as f:
            json.dump(
                {
                    'update': str(datetime.datetime.now()),
                    'total': self.twse.get_holidays()
                },
                f,
                ensure_ascii=False,
                indent=2
            )


if __name__ == '__main__':
    pass

