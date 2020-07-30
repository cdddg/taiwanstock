# 台灣上市上櫃股票爬蟲
### 抓取每日盤後交易資訊以及三大法人交易資訊

```python
from . import stock

client = stock.client.TaiwanStockClient(None)
client.fetch_to_csv(2020, 1, 1)
```

資料來源 [台灣證券交易所](https://www.twse.com.tw/zh/), [證券櫃檯買賣中心](https://www.tpex.org.tw/web/?l=zh-tw)

