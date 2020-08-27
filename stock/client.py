import csv
import datetime
import json
import os
from typing import Dict, List

import pymysql

from .box.decorators import monitor
from .foundation import tpex, twse
from .orm import adapter, models

PATH = os.path.dirname(os.path.abspath(__file__))


class TaiwanStockClient:
    '''Fetch trading information of Taiwan stocks

    抓取台股上市上櫃之每日盤後行情及三大法人買賣超

    - 台灣證券交易所
        1. rate limiting 設定，5秒內不能存取超過3次。建議至少延遲3秒，避免被ban。
        2. 每日收盤行情自 2004/02/11 開始提供資訊。
        3. 三大法人買賣超日報自 2012/05/02 起開始提供資訊。
        4. 融資融券餘額自民國 2001/01/01 起提供資訊。

    - 證券櫃檯買賣中心
        1. 每日收盤行情自 2007/01/01 起開始提供資訊。
        2. 三大法人買賣超日報自 2005/04/21 起開始提供資訊。
        3. 融資融券餘額自民國 2003/08/01 起提供資訊。

    - 配合來源資料網站

        | 抓取資料範圍                                     | 抓取支援日期 |
        | ------------------------------------------------ | ------------ |
        | `盤後行情`                                       | 2007/01/01   |
        | `盤後行情` 、 `三大買人買賣超`                   | 2012/05/02   |
        | `盤後行情` 、 `融資融券餘額`                     | 2003/08/01   |
        | `盤後行情` 、 `三大買人買賣超` 、 `融資融券餘額` | 2012/05/02   |

        1. 抓取日小於來源網站資訊提供日則 raise NotImplementedError
        2. 抓取日若為國定假日則 print(date is holiday)
    '''

    def __init__(
        self,
        version=None,
        enable_fetch_institutional_investors=False,
        enable_fetch_credit_transactions_securities=False,
        sleep_second=3
    ):
        self._version = version

        enable_fetch_price = True
        kwargs = locals().copy()
        kwargs.pop('self')
        kwargs.pop('version')
        self.tpex = tpex.TPEXFetcher(**kwargs)
        self.twse = twse.TWSEFetcher(**kwargs)

    def __create_directrory(self):
        directrory = os.path.join(PATH, 'rawdata')
        if not os.path.isdir(directrory):
            os.mkdir(directrory)
        return directrory

    @monitor
    def fetch(self, year: int, month: int, day: int) -> List[Dict]:
        rawdata = list()
        rawdata += self.twse.fetch(year, month, day)
        rawdata += self.tpex.fetch(year, month, day)
        return rawdata

    def fetch_to_csv(self, year: int, month: int, day: int, path: str = None, overwrite=True):
        if path is None:
            path = os.path.join(self.__create_directrory(), f'{year}{month:0>2}{day:0>2}.csv')

        if not os.path.isfile(path) or overwrite is True:
            rawdata = self.fetch(year, month, day)
            if rawdata is not None:
                with open(path, 'w', encoding='utf8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=rawdata[0].keys())
                    writer.writeheader()
                    writer.writerows(rawdata)

    def fetch_to_json(self, year: int, month: int, day: int, path: str = None, overwrite=True):
        if path is None:
            path = os.path.join(self.__create_directrory(), f'{year}{month:0>2}{day:0>2}.json')

        if not os.path.isfile(path) or overwrite is True:
            rawdata = self.fetch(year, month, day)
            if rawdata is not None:
                rawdata = {row['sid']: row for row in rawdata}
                with open(path, 'w', encoding='utf8') as f:
                    json.dump(
                        obj=rawdata,
                        fp=f,
                        ensure_ascii=False,
                        indent=4
                    )

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
        with open(os.path.join(PATH, 'box', 'holidays.json'), 'w+') as f:
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
