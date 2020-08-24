import urllib
from datetime import datetime
from time import sleep

import requests

from ..box.exceptions import HolidayWarning
from .base import BaseFetcher


class TWSEFetcher(BaseFetcher):
    TWSE_BASE_URL = 'http://www.twse.com.tw/'

    def __init__(
        self,
        enable_fetch_price,
        enable_fetch_institutional_investors,
        enable_fetch_credit_transactions_securities,
        sleep_second
    ):
        self._enable_fetch_price = enable_fetch_price
        self._enable_fetch_institutional_investors = enable_fetch_institutional_investors
        self._enable_fetch_credit_transactions_securities = enable_fetch_credit_transactions_securities
        self._sleep_second = sleep_second

    def adapter(self, date):
        return self.combine(
            date=date,
            price=self.__adapter_fetch_price(date),
            institutional_investors=self.__adapter_fetch_institutional_investors(date),
            credit_transactions_securities=self.__adapter_fetch_credit_transactions_securities(date)
        )

    def fetch(self, year: int, month: int, day: int) -> list:
        date = self.check_date_format(f'{year}{month:0>2}{day:0>2}')
        data = self.adapter(date)
        return data

    def get_holidays(self):
        holidays = []
        for year in range(2020, 2002 - 1, -1):
            sleep(1)
            holidays += self._get_holiday(year)
        return holidays

    def __adapter_fetch_price(self, date):
        if self._enable_fetch_price:
            sleep(self._sleep_second)
            if date < '20040211':
                raise NotImplementedError
            else:
                return self._price_20040211_now(date)
        else:
            return None

    def __adapter_fetch_institutional_investors(self, date):
        if self._enable_fetch_institutional_investors:
            sleep(self._sleep_second)
            if date < '20120502':
                raise NotImplementedError
            else:
                return self._institutional_investors_20120502_now(date)
        else:
            return None

    def __adapter_fetch_credit_transactions_securities(self, date):
        if self._enable_fetch_credit_transactions_securities:
            sleep(self._sleep_second)
            if date < '20010101':
                raise NotImplementedError
            else:
                return self._credit_transactions_securities_20010101_now(date)
        else:
            return None

    def _price_20040211_now(self, date):
        '''
        台灣證券交易所 每日收盤行情
            -- 本資訊自 民國93年2月11日 起提供
            -- https://www.twse.com.tw/exchangeReport/MI_INDEX
        '''
        # 本資訊自民國93年2月11日起提供
        resp = requests.get(
            url=urllib.parse.urljoin(self.TWSE_BASE_URL, 'exchangeReport/MI_INDEX'),
            params={
                'response': 'json',
                'date': date,
                'type': 'ALL'
            },
            headers=self.HEADERS
        )
        try:
            rawdata = resp.json()
        except Exception as e:
            print(e)
            print(resp.url)
            print(resp.text)
            raise

        if rawdata['stat'] == '很抱歉，沒有符合條件的資料!':
            raise HolidayWarning(date)

        index = '9' if 'fields9' in rawdata.keys() else '8'

        # '證券代號',
        # '證券名稱',
        # '成交股數',
        # '成交筆數',
        # '成交金額',
        # '開盤價',
        # '最高價',
        # '最低價',
        # '收盤價',
        # '漲跌(+/-)',
        # '漲跌價差',
        # '最後揭示買價',
        # '最後揭示買量',
        # '最後揭示賣價',
        # '最後揭示賣量',
        # '本益比'
        columns = rawdata[f'fields{index}']
        columns = dict(zip(columns, range(len(columns))))

        data = dict()
        for row in rawdata[f'data{index}']:
            row = [self.clean(r) for r in row]
            sid = row[columns['證券代號']]
            if self.verify_stock_id_format(id=sid) is False:
                continue

            # amplitude = re.findall(
            #     re.compile(r"<\s*p[^>]*>(.*?)<\s*/\s*p>"),
            #     row[columns['漲跌(+/-)']]
            # )
            # amplitude = '' if amplitude == [] else amplitude[0]
            # amplitude += row[columns['漲跌價差']]

            # if amplitude == '0.00':
            #     amplitude_ratio = amplitude
            # else:
            #     yesterday_price = float(row[columns['收盤價']]) - float(amplitude)
            #     amplitude_ratio = float(amplitude) / yesterday_price * 100
            #     amplitude_ratio = str(round(amplitude_ratio, 2))

            data[sid] = [
                sid,
                row[columns['證券名稱']],
                row[columns['開盤價']],
                row[columns['最高價']],
                row[columns['最低價']],
                row[columns['收盤價']],
                row[columns['成交股數']],
                row[columns['成交筆數']],
                row[columns['成交金額']],
            ]
        return data

    def _institutional_investors_20120502_now(self, date):
        '''
        台灣證券交易所 三大法人買賣超日報
            -- 本資訊自 民國101年5月2日 起提供
            -- https://www.twse.com.tw/zh/page/trading/fund/T86.html
        '''
        resp = requests.get(
            url=urllib.parse.urljoin(self.TWSE_BASE_URL, 'fund/T86'),
            params={
                'response': 'json',
                'date': date,
                'selectType': 'ALL'
            },
            headers=self.HEADERS
        )
        rawdata = resp.json()
        if rawdata['stat'] == '很抱歉，沒有符合條件的資料!':
            raise HolidayWarning(date)

        # '證券代號',
        # '證券名稱',
        # '外陸資買進股數(不含外資自營商)',
        # '外陸資賣出股數(不含外資自營商)',
        # '外陸資買賣超股數(不含外資自營商)',
        # '外資自營商買進股數', '外資自營商賣出股數',
        # '外資自營商買賣超股數',
        # '投信買進股數',
        # '投信賣出股數',
        # '投信買賣超股數',
        # '自營商買賣超股數',
        # '自營商買進股數(自行買賣)',
        # '自營商賣出股數(自行買賣)',
        # '自營商買賣超股數(自行買賣)',
        # '自營商買進股數(避險)',
        # '自營商賣出股數(避險)',
        # '自營商買賣超股數(避險)',
        # '三大法人買賣超股數'
        columns = rawdata['fields']
        columns = dict(zip(columns, range(len(columns))))

        data = dict()
        for row in rawdata['data']:
            if len(row) != len(columns.keys()):
                raise ConnectionError

            row = [self.clean(r) for r in row]
            sid = row[columns['證券代號']].replace(',', '')
            if self.verify_stock_id_format(id=sid) is False:
                continue

            data[sid] = [
                self._add(row[columns['外陸資買進股數(不含外資自營商)']], row[columns['外資自營商買進股數']]),
                self._add(row[columns['外陸資賣出股數(不含外資自營商)']], row[columns['外資自營商賣出股數']]),
                self._add(row[columns['外陸資買賣超股數(不含外資自營商)']], row[columns['外資自營商買賣超股數']]),
                row[columns['投信買進股數']],
                row[columns['投信賣出股數']],
                row[columns['投信買賣超股數']],
                self._add(row[columns['自營商買進股數(自行買賣)']], row[columns['自營商買進股數(避險)']]),
                self._add(row[columns['自營商賣出股數(自行買賣)']], row[columns['自營商賣出股數(避險)']]),
                self._add(row[columns['自營商買賣超股數(自行買賣)']], row[columns['自營商買賣超股數(避險)']]),
                row[columns['三大法人買賣超股數']],
            ]
        return data

    def _credit_transactions_securities_20010101_now(self, date):
        '''
        台灣證券交易所 每日收盤行情
            - 本資訊自民國90年01月01日起提供
            - https://www.twse.com.tw/zh/page/trading/exchange/MI_MARGN.html
        '''
        resp = requests.get(
            url=urllib.parse.urljoin(self.TWSE_BASE_URL, 'exchangeReport/MI_MARGN'),
            params={
                'response': 'json',
                'date': date,
                'selectType': 'ALL'
            },
            headers=self.HEADERS
        )
        try:
            rawdata = resp.json()
        except Exception as e:
            print(e)
            print(resp.url)
            print(resp.text)
            raise

        if rawdata['stat'] == '很抱歉，沒有符合條件的資料!':
            raise HolidayWarning(date)

        columns = [
            "股票代號",
            "股票名稱",
            "融資買進",
            "融資賣出",
            "融資現金償還",
            "融資前日餘額",
            "融資今日餘額",
            "融資限額",
            "融券買進",
            "融券賣出",
            "融券現券償還",
            "融券前日餘額",
            "融券今日餘額",
            "融券限額",
            "資券互抵",
            "註記"
        ]
        columns = dict(zip(columns, range(len(columns))))
        print(resp.url)

        data = dict()
        for row in rawdata['data']:
            row = [self.clean(r) for r in row]
            sid = row[columns['股票代號']]
            if self.verify_stock_id_format(id=sid) is False:
                continue

            data[sid] = [
                row[columns['融資買進']],
                row[columns['融資賣出']],
                row[columns['融資現金償還']],
                row[columns['融資今日餘額']],
                row[columns['融資限額']],
                row[columns['融券買進']],
                row[columns['融券賣出']],
                row[columns['融券現券償還']],
                row[columns['融券今日餘額']],
                row[columns['融券限額']],
                row[columns['資券互抵']],
                row[columns['註記']],
            ]
        return data

    def _get_holiday(self, year):
        republic_era_year = self.republic_era_datetime(str(year))
        resp = requests.get(
            url=urllib.parse.urljoin(self.TWSE_BASE_URL, 'holidaySchedule/holidaySchedule'),
            params={
                'response': 'csv',
                'queryYear': republic_era_year
            },
            headers=self.HEADERS
        )

        text = resp.text.strip().split('\n')
        rawdata = text[2:]

        columns = text[1]
        columns = [column.strip() for column in columns.split(',')]
        columns = dict(zip(columns, range(len(columns))))

        data = []
        for row in rawdata:
            row = [r.strip() for r in row.split(',')]

            date = row[columns['日期']]
            date = [d + '日' for d in date.split('日')][0:-1]
            for d in date:
                data += [
                    {
                        'date': self._convert_chinese_date(year, d),
                        'name': row[columns['名稱']],
                        'description': row[columns['說明']]
                    }
                ]
        return data

    def _add(self, x, y):
        return str(int(x) + int(y))

    def _convert_chinese_date(self, year: str, date: str):
        return str(year) + datetime.strptime(date, '%m月%d日').strftime('%m%d')
