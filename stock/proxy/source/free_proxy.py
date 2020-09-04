import datetime as dt
import json
import os

import lxml.html
import requests

JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_setting.json')


class FreeProxy:

    def __init__(self, country_id=[], timeout=0.5):
        self.country_id = country_id
        self.timeout = timeout

    def __check(self, proxies):
        with requests.get('http://www.google.com', proxies=proxies, timeout=self.timeout, stream=True) as r:
            if r.raw.connection.sock:
                if r.raw.connection.sock.getpeername()[0] == proxies['http'].split(':')[1][2:]:
                    return True

    def download(self):
        page = requests.get('https://www.sslproxies.org')
        doc = lxml.html.fromstring(page.content)
        tr_elements = doc.xpath('//*[@id="proxylisttable"]//tr')
        if not self.country_id:
            proxies_array = [
                f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}' for i in
                range(1, 101)
            ]
        else:
            proxies_array = [
                f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}' for i in
                range(1, 101)
                if tr_elements[i][2].text_content() in self.country_id
            ]
        results = []
        for address in proxies_array:
            try:
                proxies = {'http': f"http://{address}"}
                if self.__check(proxies=proxies):
                    results += [proxies]
            except requests.exceptions.RequestException as e:
                print('\n', e)
        return results

    def get(self):
        with open(JSON_PATH, 'r', encoding='utf8') as f:
            return list(map(lambda row: {'http': row}, json.load(f)['http']))

    def update(self):
        response = self.download()
        if response != []:
            with open(JSON_PATH, 'w+', encoding='utf8') as f:
                json.dump(
                    obj={
                        'updated_at': str(dt.datetime.now()),
                        'http': [f['http'] for f in response]
                    },
                    fp=f,
                    ensure_ascii=False,
                    indent=4
                )
