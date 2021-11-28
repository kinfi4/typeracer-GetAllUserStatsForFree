import re
from string import Template

import requests
import pandas as pd
from bs4 import BeautifulSoup, Tag

from src.constants import URL
from src.statistics_analysis import Statistics


class Parser:
    def __init__(self):
        self.user_data = pd.DataFrame(columns=['race', 'speed', 'accuracy', 'points', 'place', 'date'])
        self.percentage = 0.00

    def parse_user_stats(self, username) -> Statistics:
        self.print_progress()

        url = Template(URL)
        counter, next_cursor = 0, ''

        number_of_races = self._get_number_of_races(url.substitute({'user': username, 'cursor': next_cursor}))

        while True:
            data, next_cursor = self._parse_single_page(url.substitute({'user': username, 'cursor': next_cursor}))

            self.user_data = self.user_data.append(data)
            counter += 1

            self.percentage = round((counter * 100 / number_of_races) * 100, 2)
            self.percentage = self.percentage if self.percentage < 100.00 else 100.00
            self.print_progress()

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

    def _get_number_of_races(self, url):
        page = requests.get(url)
        page_soup = BeautifulSoup(page.text, 'html.parser')
        stats_table = page_soup.find('table', {'class': 'scoresTable'})

        for row in stats_table.find_all('tr')[1:]:
            race_number_tag: Tag = row.find_all('td')[0]
            return int(race_number_tag.find('a').text)

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

    def print_progress(self):
        print(f'[Parser]: {self.percentage}% parsed\r', flush=True, end='')
