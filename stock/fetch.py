# -*- coding:utf-8 -*-

import csv
import datetime as dt
import os
import urllib
from functools import wraps
from time import sleep

import requests

from stock.errors import DateError

HEADERS = {
    'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0',
    'Accept-Encoding': 'gzip, deflate, compress'
}
TWSE_BASE_URL = 'http://www.twse.com.tw/'
TPEX_BASE_URL = 'http://www.tpex.org.tw/'


def catcher(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f'{func.__qualname__}()')
        for i in range(3):
            try:
                sleep(1)
                return func(*args, **kwargs)
            except DateError as e:
                print(e)
                return
            except requests.exceptions.ConnectionError:
                sleep(30)
    return wrapper


class BaseFetcher:

    NOW_FOLDER = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]

    def __init__(self):
        # self.title_path = os.path.join(os.path.join(self.NOW_FOLDER, 'title'))
        self.rawdata_path = os.path.join(os.path.join(self.NOW_FOLDER, 'rawdata'))
        # self.results_path = os.path.join(os.path.join(self.NOW_FOLDER, 'results'))
        for _, path in vars(self).items():
            if not os.path.isdir(path):
                os.mkdir(path)


class TWSEFetcher(BaseFetcher):

    def __init__(self, str_nodash_date):
        super().__init__()
        self.date = str_nodash_date
        self.limit = '20120502'

    @property
    def volume_path(self):
        return os.path.join(self.rawdata_path, f'{self.date}_twse_volume.csv')

    @property
    def investor_path(self):
        return os.path.join(self.rawdata_path, f'{self.date}_twse_investor.csv')

    @catcher
    def download_price_valume(self):
        '''台灣證券交易所  首頁>交易資訊>盤後資訊>每日收盤行情'''
        if self.date >= '20040211':
            # 本資訊自民國93年2月11日起提供
            resp = requests.get(
                url=urllib.parse.urljoin(TWSE_BASE_URL, 'exchangeReport/MI_INDEX'),
                params={
                    'response': 'json',
                    'date': self.date,
                    'type': 'ALL'
                },
                headers=HEADERS
            )
            # print(resp.url)
            rawdata = resp.json()
            if rawdata['stat'] == '很抱歉，沒有符合條件的資料!':
                raise DateError(self.date)
            try:
                rawdata['fields9']
                column_name__fields = 'fields9'
                column_name__data = 'data9'
            except KeyError:
                column_name__fields = 'fields8'
                column_name__data = 'data8'

            # csv
            writer = csv.writer(open(self.volume_path, 'w+'))
            columns = rawdata[column_name__fields]
            data = []
            for row in rawdata[column_name__data]:
                row[2] = row[2].replace(',', '')
                row[3] = row[3].replace(',', '')
                row[4] = row[4].replace(',', '')
                row[9] = row[9].strip()
                if len(row[9]) > 1:
                    row[9] = row[9][-5]
                data += [row]
            writer.writerow(columns)
            writer.writerows(data)
        else:
            raise DateError(self.date)

    @catcher
    def institutional_investors(self):
        if self.date >= '20120502':
            resp = requests.get(
                url=urllib.parse.urljoin(TWSE_BASE_URL, 'fund/T86'),
                params={
                    'response': 'json',
                    'date': self.date,
                    'selectType': 'ALL'
                },
                headers=HEADERS
            )
            # print(resp.url)
            rawdata = resp.json()
            if rawdata['stat'] == '很抱歉，沒有符合條件的資料!':
                raise DateError(self.date)
            # csv
            writer = csv.writer(open(self.investor_path, 'w+'))
            columns = rawdata['fields']
            rows = []
            for row in rawdata['data']:
                rows += [[r.replace(',', '').strip() for r in row]]
            writer.writerow(columns)
            writer.writerows(rows)
        else:
            raise DateError(self.date)


class TPEXFetcher(BaseFetcher):

    def __init__(self, str_nodash_date):
        super().__init__()
        self.date = str_nodash_date
        date = dt.datetime.strptime(self.date, '%Y%m%d')
        self.yyyy = date.year - 1911
        self.mm = date.month
        self.dd = date.day
        self.limit = '20070701'

    @property
    def volume_path(self):
        return os.path.join(self.rawdata_path, f'{self.date}_tpex_volume.csv')

    @property
    def investor_path(self):
        return os.path.join(self.rawdata_path, f'{self.date}_tpex_investor.csv')

    @catcher
    def download_price_valume(self):
        '''證券櫃檯買賣中心 上櫃股票每日收盤行情(不含定價)'''
        # https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php?l=zh-tw

        if self.date >= '20070701':
            # 本資訊自民國96年7月起開始提供
            resp = requests.get(
                url=urllib.parse.urljoin(TPEX_BASE_URL, 'web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php'),
                params={
                    'l': 'zh-tw',
                    'o': 'json',
                    'se': 'AL',
                    'd': f'{self.yyyy}/{self.mm:02}/{self.dd:02}'
                },
                headers=HEADERS
            )
            # print(resp.url)
            rawdata = resp.json()
            if rawdata['iTotalRecords'] == 0:
                raise DateError(self.date)
            # csv
            writer = csv.writer(open(self.volume_path, 'w+'))
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
            rows = []
            for row in rawdata['aaData']:
                rows += [[r.replace(',', '').strip() for r in row]]
            writer.writerow(columns)
            writer.writerows(rows)
        # elif '20070101' <= self.date <= '20070630':
        #     raise DateError(self.date)
        else:
            raise DateError(self.date)

    @catcher
    def institutional_investors(self):
        '''證券櫃檯買賣中心'''
        # https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge.php?l=zh-tw

        if '20050421' <= self.date <= '20141130':
            resp = requests.get(
                url=urllib.parse.urljoin(TPEX_BASE_URL, 'web/stock/3insti/daily_trade/3itrade_download.php'),
                params={
                    'l': 'zh-tw',
                    'se': 'AL',
                    't': 'D',
                    'd': f'{self.yyyy}/{self.mm:02}/{self.dd:02}',
                    's': '0,asc,0'
                },
                headers=HEADERS
            )
            # print(resp.url)
            if resp.text.strip() == '代號,名稱,外資及陸資買股數,外資及陸資賣股數,外資及陸資淨買股數,投信買進股數,投信賣股數,投信淨買股數,自營商買股數,自營商賣股數,自營淨買股數,三大法人買賣超股數':
                raise DateError(self.date)

            # text = str(resp.content, 'utf-8')
            text = resp.text
            writer = csv.writer(open(self.investor_path, 'w+'))
            text = text.strip().split('\r\n')[1:]
            columns = text[0].split(',')
            rows = []
            for row in text[1:]:
                rows += [[r.replace(',', '').replace('"', '').strip() for r in row.split('",')]]
            writer.writerow(columns)
            writer.writerows(rows)

        elif self.date >= '20141201':
            resp = requests.get(
                url=urllib.parse.urljoin(TPEX_BASE_URL, 'web/stock/3insti/daily_trade/3itrade_hedge_result.php'),
                params={
                    'l': 'zh-tw',
                    'o': 'json',
                    'se': 'AL',
                    't': 'D',
                    'd': f'{self.yyyy}/{self.mm:02}/{self.dd:02}',
                    's': '0,asc'
                },
                headers=HEADERS
            )
            # print(resp.url)
            rawdata = resp.json()
            if rawdata['iTotalRecords'] == 0:
                raise DateError(self.date)
            # csv
            writer = csv.writer(open(self.investor_path, 'w+'))
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
            rows = []
            for row in rawdata['aaData']:
                rows += [[r.replace(',', '').strip() for r in row]]
            writer.writerow(columns)
            writer.writerows(rows)

        else:
            raise DateError(self.date)
