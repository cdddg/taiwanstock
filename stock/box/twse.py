import re
import urllib
from datetime import datetime
from time import sleep

import requests

from ..foundation.exceptions import HolidayWarning
from .base import BaseFetcher


class TWSEFetcher(BaseFetcher):
    TWSE_BASE_URL = 'http://www.twse.com.tw/'

    def __init__(self):
        pass

    def __adapter(self, date):
        sleep(3)
        if date < '20040211':
            raise NotImplementedError
        else:
            price = self.__price_20040211_now(date)

        sleep(3)
        if date < '20120502':
            raise NotImplementedError
        else:
            institutional_investors = self.__institutional_investors_20120502_now(date)

        return self.combine(date, price, institutional_investors)

    def __add(self, x, y):
        return str(int(x) + int(y))

    def __price_20040211_now(self, date):
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
            amplitude = re.findall(
                re.compile(r"<\s*p[^>]*>(.*?)<\s*/\s*p>"),
                row[columns['漲跌(+/-)']]
            )
            amplitude = '' if amplitude == [] else amplitude[0]
            amplitude += row[columns['漲跌價差']]

            if amplitude == '0.00':
                amplitude_ratio = amplitude
            else:
                yesterday_price = float(row[columns['收盤價']]) - float(amplitude)
                amplitude_ratio = float(amplitude) / yesterday_price * 100
                amplitude_ratio = str(round(amplitude_ratio, 2))

            data[sid] = [
                sid,
                row[columns['證券名稱']],
                row[columns['開盤價']],
                row[columns['最高價']],
                row[columns['最低價']],
                row[columns['收盤價']],
                amplitude,
                amplitude_ratio,
                row[columns['成交股數']],
                row[columns['成交筆數']],
                row[columns['成交金額']],
            ]
        return data

    def __institutional_investors_20120502_now(self, date):
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
            data[sid] = [
                self.__add(row[columns['外陸資買進股數(不含外資自營商)']], row[columns['外資自營商買進股數']]),
                self.__add(row[columns['外陸資賣出股數(不含外資自營商)']], row[columns['外資自營商賣出股數']]),
                self.__add(row[columns['外陸資買賣超股數(不含外資自營商)']], row[columns['外資自營商買賣超股數']]),
                row[columns['投信買進股數']],
                row[columns['投信賣出股數']],
                row[columns['投信買賣超股數']],
                self.__add(row[columns['自營商買進股數(自行買賣)']], row[columns['自營商買進股數(避險)']]),
                self.__add(row[columns['自營商賣出股數(自行買賣)']], row[columns['自營商賣出股數(避險)']]),
                self.__add(row[columns['自營商買賣超股數(自行買賣)']], row[columns['自營商買賣超股數(避險)']]),
                row[columns['三大法人買賣超股數']],
            ]
        return data

    def fetch(self, year: int, month: int, day: int) -> list:
        date = f'{year}{month:02}{day:02}'
        data = self.__adapter(date)
        return data

    def __get_holiday(self, year):
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
                        'date': self.__convert_chinese_date(year, d),
                        'name': row[columns['名稱']],
                        'description': row[columns['說明']]
                    }
                ]
        return data

    def __convert_chinese_date(self, year: str, date: str):
        return str(year) + datetime.strptime(date, '%m月%d日').strftime('%m%d')

    def get_holidays(self):
        holidays = []
        for year in range(2020, 2002 - 1, -1):
            sleep(1)
            holidays += self.__get_holiday(year)
        return holidays

