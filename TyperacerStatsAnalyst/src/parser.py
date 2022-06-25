import re
from string import Template

import requests
import pandas as pd
from bs4 import BeautifulSoup

from src.constants import URL
from src.statistics_analysis import StatisticsVisualizer


class Parser:
    def __init__(self):
        self.list_of_columns = ['race', 'speed', 'accuracy', 'points', 'place', 'date']
        self.user_data = pd.DataFrame(columns=self.list_of_columns)
        self.percentage = 0.00

    def parse_user_stats(self, username: str) -> StatisticsVisualizer:
        self._print_progress()

        url = Template(URL)
        counter, next_cursor = 0, ''

        number_of_races = self._get_number_of_races(url.substitute({'user': username, 'cursor': next_cursor}))

        while True:
            data, next_cursor = self._parse_single_page(url.substitute({'user': username, 'cursor': next_cursor}))

            self.user_data = self.user_data.append(data)
            counter += 1

            self.percentage = round((counter * 100 / number_of_races) * 100, 2)
            self.percentage = self.percentage if self.percentage < 100.00 else 100.00
            self._print_progress()

            if not next_cursor:  # we have reached the last table
                break

        return StatisticsVisualizer(self.user_data)

    def _parse_single_page(self, url):
        page = requests.get(url)
        page_soup = BeautifulSoup(page.text, 'html.parser')
        data_rows = page_soup.find_all('div', {'class': 'Scores__Table__Row'})

        data = []
        for row in data_rows:
            data.append(
                [
                    row.find('div', {'class': 'profileTableHeaderUniverse'}).find('a').get_text(strip=True),  # race number
                    row.find('div', {'class': 'profileTableHeaderRaces'}).get_text(strip=True).replace(' WPM', ''),  # WPM column
                    row.find('div', {'class': 'profileTableHeaderRaces'}).get_text(strip=True).replace('%', ''),  # accuracy
                    row.find('div', {'class': 'profileTableHeaderAvg'}).get_text(strip=True),  # points
                    row.find('div', {'class': 'profileTableHeaderPoints'}).get_text(strip=True),  # place
                    row.find('div', {'class': 'profileTableHeaderDate'}).get_text(strip=True),  # date
                ]
            )

        next_cursor = self._find_next_cursor(page_soup)

        return pd.DataFrame(data, columns=self.list_of_columns), next_cursor

    @staticmethod
    def _get_number_of_races(url):
        page = requests.get(url)
        page_soup = BeautifulSoup(page.text, 'html.parser')

        first_row = page_soup.find('div', {'class': 'Scores__Table__Row'})
        race_number_tag = first_row.find('div', {'class': 'profileTableHeaderUniverse'})

        return int(race_number_tag.find('a').text)

    @staticmethod
    def _find_next_cursor(page_soup):
        last_row = page_soup.find_all('div', {'class': 'Scores__Table__Row'})[-1]
        link_tags = last_row.find_next_sibling('div').find_all('a')

        next_link = None
        for link in link_tags:
            if 'load older' in link.string:
                next_link = link

        if next_link is None:  # This means that we've reached the last table
            return ''

        href = next_link.attrs.get('href')
        return re.search(r'cursor=(.*?)&', href).groups()[0]

    def _print_progress(self):
        print(f'[Parser]: {self.percentage}% parsed\r', flush=True, end='')
