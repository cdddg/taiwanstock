# 台灣上市上櫃股票爬蟲

抓取台股每日盤後及三大法人交易資訊\
Fetch trading information of Taiwan stocks

```python
from . import stock

client = stock.client.TaiwanStockClient()
```

<br>

Download csv file

```python
client.fetch_to_csv(year, month, day)
```

<br>

Insert to Sqlite

```python
client.fetch_to_sqlite(
    year,
    month,
    day,
    database_name
)
```

<br>

Insert to Mysql

```python
client.fetch_to_mysql(
    year,
    month,
    day,
    database_name,
    host,
    user,
    password,
    port
)
```

<br>

## Requirements

- [x] pip install -r `requestment.txt`
- [x] python version >= `3.6+`

