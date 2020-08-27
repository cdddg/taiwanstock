import datetime as dt

import stock


if __name__ == "__main__":
    today = dt.datetime.now()

    # initialize
    client = stock.client.TaiwanStockClient(
        enable_fetch_institutional_investors=True,
        enable_fetch_credit_transactions_securities=True,
    )
    print(client.__doc__)

    # 下載csv檔
    client.fetch_to_csv(today.year, today.month, today.day, overwrite=True)

    # 下載json檔
    client.fetch_to_json(today.year, today.month, today.day, overwrite=True)

    # 下載至sqlite資料庫
    client.fetch_to_sqlite(
        today.year, today.month, today.day,
        'splite.db'
    )

    # 下載至mysql資料庫
    client.fetch_to_mysql(
        today.year, today.month, today.day,
        database_name='',
        host='',
        user='',
        password='',
        port=None
    )
