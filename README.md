# 台灣上市上櫃股票爬蟲

**抓取台股每日盤後及三大法人交易資訊 Fetch trading information of Taiwan stocks**

```python
from . import stock

client = stock.client.TaiwanStockClient()
print(client.__doc__)

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

<br>

**Requirements [^1]**

- [x] pip install -r requestment.txt
- [x] python version >= `3.6+`

<br>

**Source [^2]**

1. [台灣證券交易所](https://www.twse.com.tw/zh/)
2. [證券櫃檯買賣中心](https://www.tpex.org.tw/web/)

<br>

[^1]: python version >= `3.6+`<br>
[^2]: 因 [台灣證券交易所 - 三大法人買賣超日報](https://www.twse.com.tw/zh/page/trading/fund/T86.html) 自民國101年5月2日起開始提供資訊，故目前抓取日期從 `2012/05/02` 開始抓取，待增加其他資訊來源。



