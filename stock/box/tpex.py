import urllib
from time import sleep

import requests

from ..foundation.exceptions import HolidayWarning
from . import base


class TPEXFetcher(base.BaseFetcher):
    TPEX_BASE_URL = 'http://www.tpex.org.tw/'

    def __init__(self):
        pass

    def fetch(self, year: int, month: int, day: int) -> list:
        date = f'{year}{month:02}{day:02}'
        data = self.__adapter(date)
        return data

    def republic_era_datetime(self, date):
        year = int(date[0:4]) - 1911
        month = date[4:6]
        day = date[6:8]
        return year, month, day

    def __adapter(self, date):
        sleep(3)
        if date < '20070101':
            raise NotImplementedError
        elif date <= '20070630':
            price = self.__price_20070101_20070630(date)
        else:
            price = self.__price_20070701_now(date)

        sleep(3)
        if date < '20050421':
            raise NotImplementedError
        elif date <= '20141130':
            institutional_investors = self.__institutional_investors_20050421_20141130(date)
        else:
            institutional_investors = self.__institutional_investors_20141201_now(date)

        return self.combine(date, price, institutional_investors)

    def __price_20070101_20070630(self, date):
        raise NotImplementedError

    def __price_20070701_now(self, date):
        year, month, day = self.republic_era_datetime(date)
        '''證券櫃檯買賣中心 上櫃股票每日收盤行情(不含定價)'''
        # 本資訊自民國96年7月起開始提供
        # https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php?l=zh-tw

        resp = requests.get(
            url=urllib.parse.urljoin(
                self.TPEX_BASE_URL,
                'web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php'
            ),
            params={
                'l': 'zh-tw',
                'o': 'json',
                'se': 'AL',
                'd': f'{year}/{month:0>2}/{day:0>2}'
            },
            headers=self.HEADERS
        )
        rawdata = resp.json()
        if rawdata['iTotalRecords'] == 0:
            raise HolidayWarning(date)

        columns = [
            '代號',
            '名稱',
            '收盤',
            '漲跌',
            '開盤',
            '最高',
            '最低',
            '成交股數',
            '成交金額(元)',
            '成交筆數',
            '最後買價',
            '最後賣價',
            '發行股數',
            '次日漲停價',
            '次日跌停價'
        ]
        columns = dict(zip(columns, range(len(columns))))

        data = dict()
        for row in rawdata['aaData']:
            row = [self.clean(v) for v in row]

            amplitude = row[columns['漲跌']]
            if amplitude in ('除息', '除權', '除權息', None):
                amplitude = None
                amplitude_ratio = '0.00'
            else:
                yesterday_price = float(row[columns['收盤']]) - float(amplitude)
                amplitude_ratio = float(amplitude) / yesterday_price * 100
                amplitude_ratio = str(round(amplitude_ratio, 2))

            sid = row[columns['代號']]
            data[sid] = [
                sid,
                row[columns['名稱']],
                row[columns['開盤']],
                row[columns['最高']],
                row[columns['最低']],
                row[columns['收盤']],
                amplitude,
                amplitude_ratio,
                row[columns['成交股數']],
                row[columns['成交筆數']],
                row[columns['成交金額(元)']],
            ]
        return data

    def __institutional_investors_20050421_20141130(self, date):
        raise NotImplementedError
        # year, month, day = self.republic_era_datetime(date)

        # # https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge.php?l=zh-tw
        # resp = requests.get(
        #     url=urllib.parse.urljoin(
        #         self.TPEX_BASE_URL,
        #         'web/stock/3insti/daily_trade/3itrade_download.php'
        #     ),
        #     params={
        #         'l': 'zh-tw',
        #         'se': 'AL',
        #         't': 'D',
        #         'd': f'{year}/{month:0>2}/{day:0>2}',
        #         's': '0,asc,0'
        #     },
        #     headers=self.HEADERS
        # )
        # text = resp.text
        # text = text.strip().split('\r\n')[1:]

        # columns = text[0].split(',')
        # data = []
        # for row in text[1:]:
        #     data += [[r.replace(',', '').replace('"', '').strip() for r in row.split('",')]]
        # return data

    def __institutional_investors_20141201_now(self, date):
        year, month, day = self.republic_era_datetime(date)

        resp = requests.get(
            url=urllib.parse.urljoin(
                self.TPEX_BASE_URL,
                'web/stock/3insti/daily_trade/3itrade_hedge_result.php'
            ),
            params={
                'l': 'zh-tw',
                'o': 'json',
                'se': 'AL',
                't': 'D',
                'd': f'{year}/{month:0>2}/{day:0>2}',
                's': '0,asc'
            },
            headers=self.HEADERS
        )
        rawdata = resp.json()
        if rawdata['iTotalRecords'] == 0:
            raise HolidayWarning(date)

        columns = [
            '代號',
            '名稱',
            '外資及陸資(不含外資自營商)-買進股數',
            '外資及陸資(不含外資自營商)-賣出股數',
            '外資及陸資(不含外資自營商)-買賣超股數',
            '外資自營商-買進股數',
            '外資自營商-賣出股數',
            '外資自營商-買賣超股數',
            '外資及陸資-買進股數',
            '外資及陸資-賣出股數',
            '外資及陸資-買賣超股數',
            '投信-買進股數',
            '投信-賣出股數',
            '投信-買賣超股數',
            '自營商(自行買賣)-買進股數',
            '自營商(自行買賣)-賣出股數',
            '自營商(自行買賣)-買賣超股數',
            '自營商(避險)-買進股數',
            '自營商(避險)-賣出股數',
            '自營商(避險)-買賣超股數',
            '自營商-買進股數',
            '自營商-賣出股數',
            '自營商-買賣超股數',
            '三大法人買賣超股數合計',
            'non'
        ]
        columns = dict(zip(columns, range(len(columns))))

        data = dict()
        for row in rawdata['aaData']:
            row = [self.clean(v) for v in row]
            sid = row[columns['代號']]
            data[sid] = [
                row[columns['外資及陸資-買進股數']],
                row[columns['外資及陸資-賣出股數']],
                row[columns['外資及陸資-買賣超股數']],
                row[columns['投信-買進股數']],
                row[columns['投信-賣出股數']],
                row[columns['投信-買賣超股數']],
                row[columns['自營商-買進股數']],
                row[columns['自營商-賣出股數']],
                row[columns['自營商-買賣超股數']],
                row[columns['三大法人買賣超股數合計']],
            ]
        return data
