import peewee


class StockInfo(peewee.Model):
    id = peewee.CharField(primary_key=True, max_length=64)
    name = peewee.CharField(max_length=64)

    class meta:
        table_name = 'stockinformation'


class StockMarket(peewee.Model):
    date = peewee.DateField(index=True)
    stock = peewee.ForeignKeyField(StockInfo)
    open = peewee.FloatField(null=True)
    high = peewee.FloatField(null=True)
    low = peewee.FloatField(null=True)
    close = peewee.FloatField(null=True)
    amplitude = peewee.FloatField(null=True)
    amplitude_ratio = peewee.FloatField()
    capacity = peewee.IntegerField()
    transaction = peewee.IntegerField()
    turnover = peewee.IntegerField()
    foreign_dealers_buy = peewee.IntegerField()
    foreign_dealers_sell = peewee.IntegerField()
    foreign_dealers_total = peewee.IntegerField()
    investment_trust_buy = peewee.IntegerField()
    investment_trust_sell = peewee.IntegerField()
    investment_trust_total = peewee.IntegerField()
    dealer_buy = peewee.IntegerField()
    dealer_sell = peewee.IntegerField()
    dealer_total = peewee.IntegerField()
    institutional_investors_total = peewee.IntegerField()

    class meta:
        table_name = 'stockmarket'
