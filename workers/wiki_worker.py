import re
from typing import Generator

from bs4 import BeautifulSoup
import requests


class WikiWorker:
    def __init__(self, url: str):
        self.url = url

    @staticmethod
    def _extract_country_name(page_html: str) -> Generator:
        soup = BeautifulSoup(page_html, "html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")
        for row in rows[1:]:
            symbol = row.find("td").text.strip("\n")
            yield re.sub(r"[^A-Za-z0-9 ]+", "", symbol)

    def get_countries(self) -> Generator:
        res = requests.get(self.url)
        res.raise_for_status()
        yield from self._extract_country_name(res.text)
