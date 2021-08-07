import csv
import re
from string import Template

import requests
from bs4 import BeautifulSoup

from project_files.constants import URL


class Statistics:
    def __init__(self, user_stats_table: list):
        self.user_stats = user_stats_table

    def save_to_file(self, filepath):
        with open(filepath, 'w') as file:
            writer = csv.DictWriter(file, self.user_stats.pop(0))

            for row in self.user_stats:
                writer.writerow(row)

    def append(self, data):
        self.user_stats.append(data)


class Parser:
    def __init__(self):
        pass

    def _parse_single_page(self, url):
        page = requests.get(url)
        page_soup = BeautifulSoup(page.text, 'html.parser')
        stats_table = page_soup.find('table', {'class': 'scoresTable'})

        rows = stats_table.find_all('tr')

        data = [tuple(element.get_text(strip=True) for element in rows[0].find_all('th')[:-1])]  # here we use
        # [:-1] because I dont want to have the last column options in my stats

        for row in rows[1:]:
            data.append(tuple(element.get_text(strip=True) for element in row.find_all('td')[:-1]))  # and here [:-1] as well

        next_cursor = self._find_next_cursor(page_soup)

        return data, next_cursor

    @staticmethod
    def _find_next_cursor(page_soup):
        next_link = page_soup.find('table', {'class': 'scoresTable'}).findNextSibling('div').find_all('span')[-1].find('a')
        href = next_link.attrs.get('href')
        return re.search(r'cursor=(.*?)&', href).groups()[0]

    def parse_user_stats(self, username) -> Statistics:
        url = Template(URL)
        data, next_cursor = self._parse_single_page(url.substitute({'user': username, 'cursor': ''}))
        print(next_cursor)


