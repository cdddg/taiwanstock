import datetime
import itertools

from ..box.constants import StockCategory
from ..box.exceptions import DateFormatError


class BaseFetcher:
    HEADERS = {
        "User-agent": "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
        "Accept-Encoding": "gzip, deflate, compress",
    }

    def __init__(
        self,
        proxy_provider,
        enable_fetch_price,
        enable_fetch_institutional_investors,
        enable_fetch_credit_transactions_securities,
        sleep_second,
    ):
        self._proxy_provider = proxy_provider
        self._enable_fetch_price = enable_fetch_price
        self._enable_fetch_institutional_investors = enable_fetch_institutional_investors
        self._enable_fetch_credit_transactions_securities = enable_fetch_credit_transactions_securities
        self._sleep_second = sleep_second

    @property
    def base_columns(self):
        return ["date", "category"]

    @property
    def price_columns(self):
        return ["sid", "name", "open", "high", "low", "close", "capacity", "transaction", "turnover"]

    @property
    def institutional_investors_columns(self):
        return [
            "foreign_dealers_buy",
            "foreign_dealers_sell",
            "foreign_dealers_total",
            "investment_trust_buy",
            "investment_trust_sell",
            "investment_trust_total",
            "dealer_buy",
            "dealer_sell",
            "dealer_total",
            "institutional_investors_total",
        ]

    @property
    def credit_transactions_securities_columns(self):
        """
        融資買進
        融資賣出
        融資現金償還
        融資今日餘額
        融資限額
        融券買進
        融券賣出
        融券現金償還
        融券今日餘額
        融券限額
        資券互抵
        註記
        """
        return [
            "margin_purchase",
            "margin_sales",
            "margin_cash_redemption",
            "margin_today_balance",
            "margin_quota",
            "short_covering",
            "short_sale",
            "short_stock_redemption",
            "short_today_balance",
            "short_quota",
            "offsetting_margin_short",
            "note",
        ]

    def get_proxy(self):
        return self._proxy_provider.get_proxy()

    def get_string_date(self, year, month, day):
        return f"{year}{month:0>2}{day:0>2}"

    def check_date_format(self, date: str):
        try:
            formatted = datetime.datetime.strptime(date, "%Y%m%d").strftime("%Y%m%d")
            if formatted != date:
                raise ValueError("{formatted} != {date}")
            else:
                return formatted
        except ValueError as e:
            raise DateFormatError from e

    def verify_stock_id_format(self, id):
        return True if len(id) == 4 else False

    def clean(self, value):
        if type(value) is str:
            if "--" in value:
                value = None
            else:
                value = (
                    value.replace(",", "")
                    .replace("⊕", "")
                    .replace("⊙", "")
                    .replace("+ ", "+")
                    .replace("- ", "-")
                    .strip()
                )
        return value

    def add(self, x, y):
        return str(int(x) + int(y))

    def combine(
        self,
        date: str,
        category: StockCategory,
        price: dict,
        institutional_investors: dict or None,
        credit_transactions_securities: dict or None,
    ) -> list:

        results = []
        for id in price.keys():
            if institutional_investors is not None and credit_transactions_securities is not None:
                result = dict(
                    itertools.zip_longest(
                        self.base_columns
                        + self.price_columns
                        + self.institutional_investors_columns
                        + self.credit_transactions_securities_columns,
                        [date, category]
                        + price[id]
                        + institutional_investors.get(id, [])
                        + credit_transactions_securities.get(id, []),
                        fillvalue="0",
                    )
                )
            elif institutional_investors is not None:
                result = dict(
                    itertools.zip_longest(
                        self.base_columns + self.price_columns + self.institutional_investors_columns,
                        [date, category] + price[id] + institutional_investors.get(id, []),
                        fillvalue="0",
                    )
                )
            elif credit_transactions_securities is not None:
                result = dict(
                    itertools.zip_longest(
                        self.base_columns + self.price_columns + self.credit_transactions_securities_columns,
                        [date, category] + price[id] + credit_transactions_securities.get(id, []),
                        fillvalue="0",
                    )
                )
            else:
                result = dict(
                    itertools.zip_longest(
                        self.base_columns + self.price_columns, [date, category] + price[id], fillvalue=None
                    )
                )

            results += [result]
        return results
