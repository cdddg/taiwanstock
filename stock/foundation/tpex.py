import urllib
from time import sleep

import requests
from bs4 import BeautifulSoup

from ..box.constants import StockCategory
from ..box.exceptions import HolidayWarning
from . import base


class TPEXFetcher(base.BaseFetcher):
    TPEX_BASE_URL = 'http://www.tpex.org.tw/'

    def __init__(
        self,
        proxy_provider,
        enable_fetch_price,
        enable_fetch_institutional_investors,
        enable_fetch_credit_transactions_securities,
        sleep_second
    ):
        super().__init__(
            proxy_provider=proxy_provider,
            enable_fetch_price=enable_fetch_price,
            enable_fetch_institutional_investors=enable_fetch_institutional_investors,
            enable_fetch_credit_transactions_securities=enable_fetch_credit_transactions_securities,
            sleep_second=sleep_second
        )

    def fetch(self, year: int, month: int, day: int) -> list:
        date = self.check_date_format(f'{year}{month:0>2}{day:0>2}')
        data = self.adapter(date)
        return data

    def adapter(self, date):
        return self.combine(
            date=date,
            category=StockCategory.TPEX.value,
            price=self.adapter_fetch_price(date),
            institutional_investors=self.adapter_fetch_institutional_investors(date),
            credit_transactions_securities=self.adapter_fetch_credit_transactions_securities(date)
        )

    def republic_era_datetime(self, date):
        year = int(date[0:4]) - 1911
        month = int(date[4:6])
        day = int(date[6:8])
        return year, month, day

    def adapter_fetch_price(self, date):
        if self._enable_fetch_price:
            sleep(self._sleep_second)
            if date < '20070101':
                raise NotImplementedError
            elif date <= '20070630':
                return self.__price_20070101_20070630(date)
            else:
                return self.__price_20070701_now(date)
        else:
            return None

    def adapter_fetch_institutional_investors(self, date):
        if self._enable_fetch_institutional_investors:
            sleep(self._sleep_second)
            if date < '20070423':
                raise NotImplementedError
            elif date <= '20141130':
                return self.__institutional_investors_20070423_20141130(date)
            else:
                return self.__institutional_investors_20141201_now(date)
        else:
            return None

    def adapter_fetch_credit_transactions_securities(self, date):
        if self._enable_fetch_credit_transactions_securities:
            if date < '20030801':
                raise NotImplementedError
            elif date <= '20061231':
                return self.__credit_transactions_securities_20030801_20061231(date)
            else:
                return self.__credit_transactions_securities_20070101_now(date)
        else:
            return None

    def __price_20070101_20070630(self, date):
        '''
        證券櫃檯買賣中心 上櫃股票每日收盤行情(不含定價)
            - 本資訊自 民國96年1-6月 起開始提供
            - https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430B/stk_wn1430.php?l=zh-tw
        '''

        year, month, day = self.republic_era_datetime(date)
        resp = requests.get(
            url=urllib.parse.urljoin(
                self.TPEX_BASE_URL,
                'web/stock/aftertrading/otc_quotes_no1430B/stk_wn1430_print.php'
            ),
            params={
                'l': 'zh-tw',
                'ajax': 'true',
                'input_date': f'{year}/{month:0>2}/{day:0>2}',
                'temp_sect': 'AL'
            },
            proxies=self.get_proxy(),
            headers=self.HEADERS
        )
        soup = BeautifulSoup(resp.text, 'lxml')

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

        text = soup.find('div', id='contentArea')
        if text is None:
            raise HolidayWarning(date)

        data = dict()
        for row in text.find_all('tr')[1:]:
            row = [self.clean(td.text) for td in row.find_all('td')]
            sid = row[columns['代號']]
            if self.verify_stock_id_format(id=sid) is False:
                continue

            data[sid] = [
                sid,
                row[columns['名稱']],
                row[columns['開盤']],
                row[columns['最高']],
                row[columns['最低']],
                row[columns['收盤']],
                row[columns['成交股數']],
                row[columns['成交筆數']],
                row[columns['成交金額(元)']],
            ]
        return data

    def __price_20070701_now(self, date):
        '''
        證券櫃檯買賣中心 上櫃股票每日收盤行情(不含定價)
            - 本資訊自民國96年7月起開始提供
            - https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php?l=zh-tw
        '''

        year, month, day = self.republic_era_datetime(date)
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
            proxies=self.get_proxy(),
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
            sid = row[columns['代號']]
            if self.verify_stock_id_format(id=sid) is False:
                continue

            data[sid] = [
                sid,
                row[columns['名稱']],
                row[columns['開盤']],
                row[columns['最高']],
                row[columns['最低']],
                row[columns['收盤']],
                row[columns['成交股數']],
                row[columns['成交筆數']],
                row[columns['成交金額(元)']],
            ]
        return data

    def __institutional_investors_20070423_20141130(self, date):
        '''
        證券櫃檯買賣中心 三大法人買賣明細資訊
            - 本資訊自 民國96年4月21日 至 103年11月30日 開始提供
            - https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade.php
            - 20070421 (星期六 國定假日)
            - 20070422 (星期日 國定假日)
        '''

        year, month, day = self.republic_era_datetime(date)

        resp = requests.get(
            url=urllib.parse.urljoin(
                self.TPEX_BASE_URL,
                'web/stock/3insti/daily_trade/3itrade_print.php'
            ),
            params={
                'l': 'zh-tw',
                'se': 'AL',
                't': 'D',
                'd': f'{year}/{month:0>2}/{day:0>2}',
                's': '0,asc,0'
            },
            proxies=self.get_proxy(),
            headers=self.HEADERS
        )
        soup = BeautifulSoup(resp.text, 'lxml')

        columns = [
            '代號',
            '名稱',
            '外資及陸資買股數',
            '外資及陸資賣股數',
            '外資及陸資淨買股數',
            '投信買進股數',
            '投信賣股數',
            '投信淨買股數',
            '自營商買股數',
            '自營商賣股數',
            '自營淨買股數',
            '三大法人買賣超股數'
        ]
        columns = dict(zip(columns, range(len(columns))))

        text = soup.find('tbody').find_all('tr')
        if text == []:
            raise HolidayWarning(date)

        data = dict()
        for row in text:
            row = [self.clean(td.text) for td in row.find_all('td')]
            sid = row[columns['代號']]
            if self.verify_stock_id_format(id=sid) is False:
                continue

            data[sid] = [
                row[columns['外資及陸資買股數']],
                row[columns['外資及陸資賣股數']],
                row[columns['外資及陸資淨買股數']],
                row[columns['投信買進股數']],
                row[columns['投信賣股數']],
                row[columns['投信淨買股數']],
                row[columns['自營商買股數']],
                row[columns['自營商賣股數']],
                row[columns['自營淨買股數']],
                row[columns['三大法人買賣超股數']],
            ]
        return data

    def __institutional_investors_20141201_now(self, date):
        '''
        證券櫃檯買賣中心 三大法人買賣明細資訊
            -- 本資訊自 民國103年12月01日 起開始提供
            -- https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge.php
        '''

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
            proxies=self.get_proxy(),
            headers=self.HEADERS
        )
        rawdata = resp.json()
        if rawdata['iTotalRecords'] == 0:
            raise HolidayWarning(date)

        if date < '20180115':
            # 107年01月12日 三大法人日交易資訊(含普通股、鉅額、零股、綜合帳戶之投信買賣成交量)依股票代碼排序
            # 107年01月13日 國定假日
            # 107年01月14日 國定假日
            columns = [
                '代號',
                '名稱',
                '外資及陸資買股數',
                '外資及陸資賣股數',
                '外資及陸資淨買股數',
                '投信買股數',
                '投信賣股數',
                '投信淨買股數',
                '自營商淨買股數',
                '自營商(自行買賣)買股數',
                '自營商(自行買賣)賣股數',
                '自營商(自行買賣)淨買股數',
                '自營商(避險)買股數',
                '自營商(避險)賣股數',
                '自營商(避險)淨買股數',
                '三大法人買賣超股數'
            ]
            columns = dict(zip(columns, range(len(columns))))
            data = dict()
            for row in rawdata['aaData']:
                row = [self.clean(v) for v in row]
                sid = row[columns['代號']]
                if self.verify_stock_id_format(id=sid) is False:
                    continue
                data[sid] = [
                    row[columns['外資及陸資買股數']],
                    row[columns['外資及陸資賣股數']],
                    row[columns['外資及陸資淨買股數']],
                    row[columns['投信買股數']],
                    row[columns['投信賣股數']],
                    row[columns['投信淨買股數']],
                    self.add(row[columns['自營商(自行買賣)買股數']], row[columns['自營商(避險)買股數']]),
                    self.add(row[columns['自營商(自行買賣)賣股數']], row[columns['自營商(避險)賣股數']]),
                    self.add(row[columns['自營商(自行買賣)淨買股數']], row[columns['自營商(避險)淨買股數']]),
                    row[columns['三大法人買賣超股數']],
                ]
            return data

        else:
            # 107年01月15日 三大法人日交易資訊(含普通股、鉅額、零股、綜合帳戶之投信買賣成交量)依股票代碼排序
            columns = [
                '代號',
                '名稱',
                '外資及陸資(不含外資自營商)買進股數',
                '外資及陸資(不含外資自營商)賣出股數',
                '外資及陸資(不含外資自營商)買賣超股數',
                '外資自營商買進股數',
                '外資自營商賣出股數',
                '外資自營商買賣超股數',
                '外資及陸資買進股數',
                '外資及陸資賣出股數',
                '外資及陸資買賣超股數',
                '投信買進股數',
                '投信賣出股數',
                '投信買賣超股數',
                '自營商(自行買賣)買進股數',
                '自營商(自行買賣)賣出股數',
                '自營商(自行買賣)買賣超股數',
                '自營商(避險)買進股數',
                '自營商(避險)賣出股數',
                '自營商(避險)買賣超股數',
                '自營商買進股數',
                '自營商賣出股數',
                '自營商買賣超股數',
                '三大法人買賣超股數合計',
                'non'
            ]
            columns = dict(zip(columns, range(len(columns))))
            data = dict()
            for row in rawdata['aaData']:
                row = [self.clean(v) for v in row]
                sid = row[columns['代號']]
                if self.verify_stock_id_format(id=sid) is False:
                    continue
                data[sid] = [
                    row[columns['外資及陸資買進股數']],
                    row[columns['外資及陸資賣出股數']],
                    row[columns['外資及陸資買賣超股數']],
                    row[columns['投信買進股數']],
                    row[columns['投信賣出股數']],
                    row[columns['投信買賣超股數']],
                    row[columns['自營商買進股數']],
                    row[columns['自營商賣出股數']],
                    row[columns['自營商買賣超股數']],
                    row[columns['三大法人買賣超股數合計']],
                ]
            return data

    def __credit_transactions_securities_20030801_20061231(self, date):
        raise NotImplementedError

    def __credit_transactions_securities_20070101_now(self, date):
        '''
        證券櫃檯買賣中心 上櫃股票融資融券餘額
            - 本資訊自民國96年1月起開始提供
            - https://www.tpex.org.tw/web/stock/margin_trading/margin_balance/margin_bal.php?l=zh-tw
        '''

        year, month, day = self.republic_era_datetime(date)

        resp = requests.get(
            url=urllib.parse.urljoin(
                self.TPEX_BASE_URL,
                'web/stock/margin_trading/margin_balance/margin_bal_result.php?'
            ),
            params={
                'l': 'zh-tw',
                'o': 'html',
                'd': f'{year}/{month:0>2}/{day:0>2}',
                's': '0,asc'
            },
            proxies=self.get_proxy(),
            headers=self.HEADERS
        )
        try:
            rawdata = resp.json()
        except Exception as e:
            print(f'--{type(e)}', e)
            print(resp.url)
            print(resp.text)
            raise
        if rawdata['aaData'] == []:
            raise HolidayWarning(date)

        columns = [
            "代號",
            "名稱",
            "融資前資餘額(張)",
            "融資資買",
            "融資資賣",
            "融資現償",
            "融資資餘額",
            "融資資屬證金",
            "融資資使用率(%)",
            "融資資限額",
            "融券前資餘額(張)",
            "融券資買",
            "融券資賣",
            "融券現償",
            "融券資餘額",
            "融券資屬證金",
            "融券資使用率(%)",
            "融券資限額",
            "資券相抵(張)",
            "備註",
        ]
        columns = dict(zip(columns, range(len(columns))))

        data = dict()
        for row in rawdata['aaData']:
            row = [self.clean(r) for r in row]
            sid = row[columns['代號']]
            if self.verify_stock_id_format(id=sid) is False:
                continue

            data[sid] = [
                row[columns['融資資買']],
                row[columns['融資資賣']],
                row[columns['融資現償']],
                row[columns['融資資餘額']],
                row[columns['融資資限額']],
                row[columns['融券資買']],
                row[columns['融券資賣']],
                row[columns['融券現償']],
                row[columns['融券資餘額']],
                row[columns['融券資限額']],
                row[columns['資券相抵(張)']],
                row[columns['備註']],
            ]
        return data
