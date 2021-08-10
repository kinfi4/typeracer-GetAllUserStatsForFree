import re
from string import Template

import requests
import pandas as pd
from bs4 import BeautifulSoup

from project_files.constants import URL
from project_files.statistics_analysis import Statistics


class Parser:
    def __init__(self):
        self.user_data = pd.DataFrame(columns=['race', 'speed', 'accuracy', 'points', 'place', 'date'])

    def parse_user_stats(self, username) -> Statistics:
        url = Template(URL)
        counter, next_cursor = 0, ''

        while True:
            data, next_cursor = self._parse_single_page(url.substitute({'user': username, 'cursor': next_cursor}))

            self.user_data = self.user_data.append(data)
            counter += 1

            print(f'Page {counter} parsed\r', flush=True, end='')

            if not next_cursor:  # we have reached the last table
                break

        return Statistics(self.user_data)

    def _parse_single_page(self, url):
        page = requests.get(url)
        page_soup = BeautifulSoup(page.text, 'html.parser')
        stats_table = page_soup.find('table', {'class': 'scoresTable'})

        rows = stats_table.find_all('tr')

        data = []
        for row in rows[1:]:  # 1: so we skip the first row, of th
            row_stack = []
            for element in row.find_all('td')[:-1]:
                if ' WPM' in element.get_text(strip=True):
                    row_stack.append(element.get_text(strip=True).replace(' WPM', ''))
                elif '%' in element.get_text(strip=True):
                    row_stack.append(element.get_text(strip=True).replace('%', ''))
                else:
                    row_stack.append(element.get_text(strip=True))

            data.append(row_stack)

        next_cursor = self._find_next_cursor(page_soup)

        return pd.DataFrame(data, columns=['race', 'speed', 'accuracy', 'points', 'place', 'date']), next_cursor

    @staticmethod
    def _find_next_cursor(page_soup):
        links = page_soup.find('table', {'class': 'scoresTable'}).findNextSibling('div').find_all('a')

        next_link = None
        for link in links:
            if 'load older' in link.string:
                next_link = link

        if next_link is None:  # This means that we've reached the last table
            return ''

        href = next_link.attrs.get('href')
        return re.search(r'cursor=(.*?)&', href).groups()[0]
