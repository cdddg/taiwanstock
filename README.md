# 台灣上市上櫃股票爬蟲

**抓取台股每日盤後及三大法人交易資訊 Fetch trading information of Taiwan stocks**

```python
from . import stock

client = stock.client.TaiwanStockClient()
```

**Download csv file**

```python
client.fetch_to_csv(year, month, day)
```

**Insert to Sqlite**

```python
client.fetch_to_sqlite(
    year, month, day,
    database_name
)
```

**Insert to Mysql**

```python
client.fetch_to_mysql(
    year, month, day,
    database_name,
    host,
    user,
    password,
    port
)
```

**Requirements**

- [x] pip install -r requestment.txt
- [x] python >= `3.6+`

