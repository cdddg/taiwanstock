# 台灣上市上櫃股票爬蟲
### 抓取每日盤後交易資訊以及三大法人交易資訊

```sh
python3 main.py
```

```python
if __name__ == "__main__":
    client = stock.client.TaiwanStockClient(None)

    start, end = dt.datetime(2020, 2, 3), dt.datetime(2020, 2, 3)

    while 1:
        client.fetch_to_csv(start.year, start.month, start.day)
        if start < end:
            start += dt.relativedelta(days=1)
        else:
            break
```

資料來源 [台灣證券交易所](https://www.twse.com.tw/zh/), [證券櫃檯買賣中心](https://www.tpex.org.tw/web/?l=zh-tw)

