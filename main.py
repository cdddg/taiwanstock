import datetime as dt
import stock


if __name__ == "__main__":
    client = stock.client.TaiwanStockClient(None)

    start, end = dt.datetime(2020, 2, 3), dt.datetime(2020, 2, 3)

    while 1:
        client.fetch_to_csv(start.year, start.month, start.day)
        if start < end:
            start += dt.relativedelta(days=1)
        else:
            break
