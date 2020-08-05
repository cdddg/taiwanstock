import csv
import datetime
import json
import os

import pymysql

from typing import Dict, List

from .box import tpex, twse
from .foundation.decorator import monitor
from .orm import adapter, models

PATH = os.path.dirname(os.path.abspath(__file__))


class TaiwanStockClient:
    '''Fetch trading information of Taiwan stocks'''

    def __init__(self, version):
        self._version = version
        self.tpex = tpex.TPEXFetcher()
        self.twse = twse.TWSEFetcher()

    @monitor
    def fetch(self, year: int, month: int, day: int) -> List[Dict]:
        rawdata = list()
        rawdata += self.twse.fetch(year, month, day)
        rawdata += self.tpex.fetch(year, month, day)
        return rawdata

    def fetch_to_csv(self, year: int, month: int, day: int, path: str = None):
        if path is not None:
            directrory = os.path.join(PATH, 'rawdata')
            if not os.path.isdir(directrory):
                os.mkdir(directrory)
            path = os.path.join(directrory, f'{year}{month:02}{day:02}.csv')

        if not os.path.isfile(path):
            rawdata = self.fetch(year, month, day)
            if rawdata is None:
                return
            with open(path, 'w', encoding='utf8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=rawdata[0].keys())
                writer.writeheader()
                writer.writerows(rawdata)

    def __bulk_insert(self, db, year, month, day):
        models.StockInfo.bind(db)
        models.StockInfo.create_table()
        models.StockMarket.bind(db)
        models.StockMarket.create_table()

        models.StockMarket \
            .delete() \
            .where(models.StockMarket.date == f'{year}{month:02}{day:02}') \
            .execute()

        data = self.fetch(year, month, day)
        rows = []
        for row in data:
            sid = row.pop('sid')
            name = row.pop('name')
            row['stock_id'] = sid
            rows += [row]

            models.StockInfo.get_or_create(id=sid, name=name)
        models.StockMarket.insert_many(rows).execute()
        return

    def fetch_to_sqlite(self, year: int, month: int, day: int, database_name=None):
        db = adapter.SQLAdapter.sqlite(
            **({'database_name': database_name} if database_name else {})
        )
        self.__bulk_insert(db, year, month, day)

    def fetch_to_mysql(self, year: int, month: int, day: int, database_name, host, user, password, port=3306):
        # create mysql databse
        try:
            conn = pymysql.connect(host=host, user=user, password=password)
            conn.cursor().execute(
                f'CREATE DATABASE {database_name} default character set utf8mb4 collate utf8mb4_unicode_ci;'
            )
        except pymysql.err.ProgrammingError:
            pass
        finally:
            conn.close()

        db = adapter.SQLAdapter.mysql(
            database_name=database_name,
            host=host,
            user=user,
            password=password,
            port=port
        )
        self.__bulk_insert(db, year, month, day)

    def fetch_to_postgresql(self, database_obj):
        raise NotImplementedError

    def get_holidays_to_csv(self):
        with open(os.path.join(PATH, 'foundation', 'holidays.json'), 'w+') as f:
            json.dump(
                obj={
                    'update': str(datetime.datetime.now()),
                    'total': self.twse.get_holidays()
                },
                fp=f,
                ensure_ascii=False,
                indent=2
            )


if __name__ == '__main__':
    pass
