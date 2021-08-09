import csv
import re
from string import Template

import requests
from bs4 import BeautifulSoup

from project_files.constants import URL


class Statistics:
    def __init__(self, user_stats_table: list):
        self.user_stats = user_stats_table

    @classmethod
    def get_stats_from_csv(cls, filename):
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            return cls(list(reader))

    def save_to_file(self, filepath):
        with open(filepath, 'w') as file:
            writer = csv.writer(file)
            writer.writerows(self.user_stats)

    def append(self, data):
        self.user_stats.append(data)

    def __str__(self):
        return f'Stats: {self.user_stats[0]}'


class Parser:
    def __init__(self):
        self.user_data = []

    def parse_user_stats(self, username) -> Statistics:
        url, next_cursor = Template(URL), ''

        self.user_data.append(self._parse_table_head(url.substitute({'user': username, 'cursor': ''})))
        counter = 0

        while True:
            data, next_cursor = self._parse_single_page(url.substitute({'user': username, 'cursor': next_cursor}))
            self.user_data.extend(data)
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
            data.append(tuple(element.get_text(strip=True) for element in row.find_all('td')[:-1]))  # [:-1] so we dont get the last column

        next_cursor = self._find_next_cursor(page_soup)

        return data, next_cursor

    @staticmethod
    def _parse_table_head(url):
        page = requests.get(url)
        rows = BeautifulSoup(page.text, 'html.parser').find('table', {'class': 'scoresTable'}).find_all('tr')

        return tuple(element.get_text(strip=True) for element in rows[0].find_all('th')[:-1])  # here we use
        # [:-1] because I dont want to have the last column "options" in my stats

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
