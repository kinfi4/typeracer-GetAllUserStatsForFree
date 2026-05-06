import re
from string import Template
from typing import Iterator

import requests
from bs4 import BeautifulSoup

from src.constants import URL
from src.exceptions import ServerTooManyRequestsError
from src.retry_decorator import retry


class HtmlFetcher:
    def __init__(self, session: requests.Session):
        self._session = session

    def fetch_pages(self, username: str) -> Iterator[str]:
        url_template = Template(URL)
        cursor = ''
        total_races = self._get_total_races(url_template.substitute(user=username, cursor=''))
        page_num = 0

        while True:
            url = url_template.substitute(user=username, cursor=cursor)
            html_text = self._load_page(url)
            page_num += 1

            percentage = min(round(page_num * 100 / total_races * 100, 2), 100.0)
            print(f'[Parser]: {percentage}% of all your races parsed\r', flush=True, end='')

            yield html_text

            cursor = self._extract_cursor(html_text)
            if not cursor:
                print()
                break

    def _get_total_races(self, url: str) -> int:
        page = self._session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        first_row = soup.find('div', {'class': 'Scores__Table__Row'})
        race_number_tag = first_row.find('div', {'class': 'profileTableHeaderUniverse'})
        return int(race_number_tag.find('a').text)

    @retry(max_retries=3, context='Retrying to load the page with stats, because internet issue')
    def _load_page(self, url: str) -> str:
        response = self._session.get(url)

        if response.status_code == 429:
            raise ServerTooManyRequestsError("Couldn't load the page.")

        if not response.ok:
            raise RuntimeError('Something went wrong during page loading...')

        return response.text

    @staticmethod
    def _extract_cursor(html_text: str) -> str:
        soup = BeautifulSoup(html_text, 'html.parser')
        for link in soup.find_all('a'):
            if 'load older' in link.get_text():
                href = link.attrs.get('href', '')
                match = re.search(r'cursor=([^&]+)', href)
                if match:
                    return match.group(1)
        return ''
