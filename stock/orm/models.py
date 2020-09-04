import peewee


class StockInfo(peewee.Model):
    id = peewee.CharField(primary_key=True, max_length=64)
    name = peewee.CharField(max_length=64)

    class meta:
        table_name = 'stock_information'


class StockMarket(peewee.Model):
    date = peewee.DateField(index=True)
    category = peewee.IntegerField()

    stock = peewee.ForeignKeyField(StockInfo)
    open = peewee.FloatField(null=True)
    high = peewee.FloatField(null=True)
    low = peewee.FloatField(null=True)
    close = peewee.FloatField(null=True)
    capacity = peewee.BigIntegerField(null=True)
    transaction = peewee.BigIntegerField(null=True)
    turnover = peewee.BigIntegerField(null=True)

    foreign_dealers_buy = peewee.BigIntegerField(null=True)
    foreign_dealers_sell = peewee.BigIntegerField(null=True)
    foreign_dealers_total = peewee.BigIntegerField(null=True)
    investment_trust_buy = peewee.BigIntegerField(null=True)
    investment_trust_sell = peewee.BigIntegerField(null=True)
    investment_trust_total = peewee.BigIntegerField(null=True)
    dealer_buy = peewee.BigIntegerField(null=True)
    dealer_sell = peewee.BigIntegerField(null=True)
    dealer_total = peewee.BigIntegerField(null=True)
    institutional_investors_total = peewee.BigIntegerField(null=True)

    margin_purchase = peewee.BigIntegerField(null=True)
    margin_sales = peewee.BigIntegerField(null=True)
    margin_cash_redemption = peewee.BigIntegerField(null=True)
    margin_today_balance = peewee.BigIntegerField(null=True)
    margin_quota = peewee.BigIntegerField(null=True)
    short_covering = peewee.BigIntegerField(null=True)
    short_sale = peewee.BigIntegerField(null=True)
    short_stock_redemption = peewee.BigIntegerField(null=True)
    short_today_balance = peewee.BigIntegerField(null=True)
    short_quota = peewee.BigIntegerField(null=True)
    offsetting_margin_short = peewee.BigIntegerField(null=True)
    note = peewee.BigIntegerField(null=True)

    class meta:
        table_name = 'stock_market'
