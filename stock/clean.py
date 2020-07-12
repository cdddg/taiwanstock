from stock.fetch import TPEXFetcher, TWSEFetcher
import csv
import os


def cleaner(date):
    print('cleaner()')

    columns = [
        'sid',
        'name',
        'volume',
        'transaction',
        'value',
        'open',
        'high',
        'low',
        'close',
        'pe_ratio',
        'foreign_dealers_buy',
        'foreign_dealers_sell',
        'foreign_dealers_total',
        'investment_trust_buy',
        'investment_trust_sell',
        'investment_trust_total',
        'dealer_buy',
        'dealer_sell',
        'dealer_total',
        'institutional_investors_total'
    ]
    results_path = os.path.join(TWSEFetcher(None).rawdata_path, f'{date}.csv')
    results = open(results_path, 'w+', newline='')
    writer = csv.DictWriter(results, fieldnames=columns)
    writer.writeheader()

    try:
        data = {}
        for path in [TWSEFetcher(date).volume_path, TPEXFetcher(date).volume_path]:
            with open(path, newline='') as f:
                for row in csv.DictReader(f, delimiter=','):
                    sid = row.get('證券代號', row.get('代號'))
                    data[sid] = [
                        row.get('證券代號', row.get('代號')),
                        row.get('證券名稱', row.get('名稱')),
                        row.get('成交股數', row.get('成交股數')).replace(',', ''),
                        row.get('成交筆數', row.get('成交筆數')).replace(',', ''),
                        row.get('成交金額', row.get('成交金額(元)')).replace(',', ''),
                        row.get('開盤價', row.get('開盤')).replace('-', ''),
                        row.get('最高價', row.get('最高')).replace('-', ''),
                        row.get('最低價', row.get('最低')).replace('-', ''),
                        row.get('收盤價', row.get('收盤')).replace('-', ''),
                        row.get('本益比', '').replace('-', ''),
                    ]

        for path in [TWSEFetcher(date).investor_path, TPEXFetcher(date).investor_path]:
            with open(path, newline='') as f:
                for row in csv.DictReader(f, delimiter=','):
                    sid = row.get('證券代號', row.get('代號'))
                    data[sid] += [
                        row.get('外資買進股數', row.get('外資及陸資買股數')),
                        row.get('外資賣出股數', row.get('外資及陸資賣股數')),
                        row.get('外資買賣超股數', row.get('外資及陸資淨買股數')),
                        row.get('投信買進股數', row.get('投信買進股數')),
                        row.get('投信賣出股數', row.get('投信賣股數')),
                        row.get('投信買賣超股數', row.get('投信淨買股數')),
                        row.get('自營商買賣超股數', row.get('自營商買股數')),
                        row.get('自營商買進股數', row.get('自營商賣股數')),
                        row.get('自營商賣出股數', row.get('自營淨買股數')),
                        row.get('三大法人買賣超股數', row.get('三大法人買賣超股數')),
                    ]
    except Exception:
        os.remove(results_path)
    else:
        data = dict(sorted(data.items(), key=lambda d: d[0], reverse=False))
        data = dict(sorted(data.items(), key=lambda d: len(d[0]), reverse=False))
        for k, v in data.items():
            writer.writerow(dict(zip(columns, v)))
    finally:
        results.close()
