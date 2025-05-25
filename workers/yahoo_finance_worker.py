import random
import threading
import time

import requests
from lxml import html

from config import URL_YAHOO_FINANCE, XPATH_YAHOO_FINANCE


class YahooFinanceWorker:
    def __init__(self, symbol: str):
        self.base_url = URL_YAHOO_FINANCE
        self.xpath = XPATH_YAHOO_FINANCE  # xpath to the element we want to extract
        self.symbol = symbol
        self._url = self.base_url.format(symbol=self.symbol)

    def get_prince(self) -> float:
        res = requests.get(self._url)
        res.raise_for_status()
        dom = html.fromstring(res.text)
        price = float(dom.xpath(self.xpath)[0].text.replace(",", ""))
        return price


class YahooFinanceScheduler(threading.Thread):
    def __init__(self, queue, **kwargs):
        super(YahooFinanceScheduler, self).__init__(**kwargs)
        self.queue = queue
        self.start()

    def run(self):
        while True:
            value = self.queue.get()
            if value.lower() == "done":
                break
            worker = YahooFinanceWorker(symbol=value)
            try:
                price = worker.get_prince()
                print(price)
            except requests.exceptions.HTTPError as e:
                print(e)
                continue
            # Time to sleep to avoid being banned
            time.sleep(random.random())
