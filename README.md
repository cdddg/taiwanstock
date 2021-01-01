# 台灣上市上櫃股票爬蟲

| 抓取資料範圍                                     | 抓取支援日期 |
| ------------------------------------------------ | ------------ |
| `盤後行情`                                       | `2007/01/01` |
| `盤後行情` 、 `三大買人買賣超`                   | `2012/05/02` |
| `盤後行情` 、 `融資融券餘額`                     | `2007/01/01` |
| `盤後行情` 、 `三大買人買賣超` 、 `融資融券餘額` | `2012/05/02` |

<br>

**Initialize**

```python
from . import stock

client = stock.client.TaiwanStockClient(
    proxy_provider=stock.proxy.provider.NoProxyProvier(),
    enable_fetch_institutional_investors=True,
    enable_fetch_credit_transactions_securities=True,
)
print(client.__doc__)

```

**Download csv file**

```python
client.fetch_to_csv(year, month, day)
```

**Download json file**

```python
client.fetch_to_json(year, month, day)
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

<br>

**Source**

1. [台灣證券交易所](https://www.twse.com.tw/zh/)
2. [證券櫃檯買賣中心](https://www.tpex.org.tw/web/)

<br>

[^1]: python version >= `3.6+`<br>
