from typing import Generator

from bs4 import BeautifulSoup
import requests


class WikiWorker:
    def __init__(self, url: str):
        self.url = url

    @staticmethod
    def _extract_company_symbol(page_html: str) -> Generator:
        soup = BeautifulSoup(page_html, "html.parser")
        table = soup.find("table", {"id": "constituents"})
        rows = table.find_all("tr")
        for row in rows[1:]:
            symbol = row.find("td").text.strip("\n")
            yield symbol

    def get_companies_500SP(self) -> Generator:
        res = requests.get(self.url)
        res.raise_for_status()
        yield from self._extract_company_symbol(res.text)
