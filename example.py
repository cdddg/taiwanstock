from datetime import datetime

import stock


if __name__ == "__main__":
    today = datetime.now()

    # initialize
    client = stock.client.TaiwanStockClient()
    print(client.__doc__)

    # 下載csv檔
    client.fetch_to_csv(today.year, today.month, today.day)

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
