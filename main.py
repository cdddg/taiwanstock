import datetime as dt

from stock.fetch import TWSEFetcher, TPEXFetcher
from stock.clean import cleaner


def downloader(date):
    # download
    twse = TWSEFetcher(date)
    tpex = TPEXFetcher(date)

    if date < twse.limit or date < tpex.limit:
        print('--RestrictedStartDate', max([twse.limit, tpex.limit]))
        return

    twse.download_price_valume()
    twse.institutional_investors()
    tpex.download_price_valume()
    tpex.institutional_investors()

    # check
    status = [
        twse.volume_path,
        twse.investor_path,
        tpex.volume_path,
        tpex.investor_path,
    ]
    if all(status):
        pass
    elif not any(status):
        pass
    else:
        print('--error', date)


if __name__ == "__main__":
    start, end = dt.datetime(2020, 2, 3), dt.datetime(2020, 2, 3)
    while 1:
        print('-* ' * 30)
        print(start)
        date = start.strftime('%Y%m%d')
        downloader(date)
        cleaner(date)
        if start < end:
            start += dt.relativedelta(days=1)
        else:
            break
