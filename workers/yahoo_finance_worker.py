import random
import threading
import time
from dataclasses import dataclass
from datetime import datetime

import requests

from config import URL_COUNTRY_INFO


def filter_kwargs(cls, kwargs):
    # Only keep keys that are fields of the dataclass
    field_names = {f.name for f in cls.__dataclass_fields__.values()}
    return {k: v for k, v in kwargs.items() if k in field_names}


@dataclass
class CountryInfo:
    name: str
    capital: str
    population: int


class YahooFinanceWorker:
    def __init__(self, symbol: str):
        self.base_url = URL_COUNTRY_INFO
        self.symbol = symbol
        self._url = self.base_url.format(symbol=self.symbol)

    def get_country_info(self) -> CountryInfo:
        res = requests.get(self._url)
        res.raise_for_status()
        data = res.json()["data"]
        return CountryInfo(**filter_kwargs(CountryInfo, data))


class YahooFinanceScheduler(threading.Thread):
    def __init__(self, queue, output_queue, **kwargs):
        super(YahooFinanceScheduler, self).__init__(**kwargs)
        self.queue = queue
        self.output_queue = output_queue
        self.start()

    def run(self):
        while True:
            value = self.queue.get()
            if value.lower() == "done":
                if self.output_queue:
                    self.output_queue.put("done")
                break
            worker = YahooFinanceWorker(symbol=value)
            try:
                country = worker.get_country_info()  # Corrected method name
                if self.output_queue:
                    self.output_queue.put(
                        (
                            country.name,
                            country.capital,
                            country.population,
                            datetime.now(),
                        )
                    )
            except requests.exceptions.HTTPError as e:
                print(e)
                continue
            # Time to sleep to avoid being banned
            time.sleep(random.random())
