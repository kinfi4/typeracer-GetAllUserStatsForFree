import re
from datetime import date
from string import Template
from typing import Optional, Tuple

import requests
import pandas as pd
from bs4 import BeautifulSoup
from dateutil.parser import parse

from src.constants import URL
from src.retry_decorator import retry
from src.exceptions import ServerTooManyRequestsError
from src.statistics_analysis import StatisticsVisualizer


class Parser:
    def __init__(self, start_date: Optional[date], end_date: Optional[date]):
        self._list_of_columns = ['race', 'speed', 'accuracy', 'points', 'place', 'date']
        self._user_data: pd.DataFrame = pd.DataFrame(columns=self._list_of_columns)
        self._percentage = 0.00

        self._start_date = start_date
        self._end_date = end_date

    def parse_user_stats(self, username: str) -> StatisticsVisualizer:
        url = Template(URL)
        counter, next_cursor = 0, ''

        number_of_races = self._get_number_of_races(url.substitute({'user': username, 'cursor': next_cursor}))

        while True:
            data, next_cursor = self._parse_single_page(url.substitute({'user': username, 'cursor': next_cursor}))

            self._user_data = self._user_data.append(data)
            counter += 1

            self._print_progress(counter, number_of_races)

            if self._start_date and self._user_data['date'].min() < self._start_date:  # we already parsed everything we needed
                break

            if not next_cursor:  # we have reached the last table
                break

        self._user_data = self._filter_out_races_by_dates(self._user_data)

        return StatisticsVisualizer(self._user_data)

    def _parse_single_page(self, url: str) -> Tuple[pd.DataFrame, str]:
        page_text_loader = retry(
            max_retries=3,
            context=f"Retrying to load the page with stats, because internet issue"
        )(self._load_page_text)

        page_text = page_text_loader(url)
        page_soup = BeautifulSoup(page_text, 'html.parser')
        data_rows = page_soup.find_all('div', {'class': 'Scores__Table__Row'})

        data = []
        for row in data_rows:
            date_str = row.find('div', {'class': 'profileTableHeaderDate'}).get_text(strip=True)  # date
            date_obj = self._parse_date(date_str)

            data.append(
                [
                    row.find('div', {'class': 'profileTableHeaderUniverse'}).find('a').get_text(strip=True),  # race number
                    row.find('div', {'class': 'profileTableHeaderRaces'}).get_text(strip=True).replace(' WPM', ''),  # WPM column
                    row.find('div', {'class': 'profileTableHeaderRaces'}).get_text(strip=True).replace('%', ''),  # accuracy
                    row.find('div', {'class': 'profileTableHeaderAvg'}).get_text(strip=True),  # points
                    row.find('div', {'class': 'profileTableHeaderPoints'}).get_text(strip=True),  # place
                    date_obj,  # date
                ]
            )

        next_cursor = self._find_next_cursor(page_soup)

        return pd.DataFrame(data, columns=self._list_of_columns), next_cursor

    def _print_progress(self, number_of_parsed_pages: int, total_number_of_races: int):
        self._percentage = round((number_of_parsed_pages * 100 / total_number_of_races) * 100, 2)
        self._percentage = self._percentage if self._percentage < 100.00 else 100.00

        print(f'[Parser]: {self._percentage}% of all your races parsed\r', flush=True, end='')

    def _filter_out_races_by_dates(self, races_data: pd.DataFrame) -> pd.DataFrame:
        if self._start_date:
            races_data = races_data[races_data['date'] > self._start_date]

        if self._end_date:
            races_data = races_data[races_data['date'] <= self._end_date]

        return races_data

    @staticmethod
    def _get_number_of_races(url: str):
        page = requests.get(url)
        page_soup = BeautifulSoup(page.text, 'html.parser')

        first_row = page_soup.find('div', {'class': 'Scores__Table__Row'})
        race_number_tag = first_row.find('div', {'class': 'profileTableHeaderUniverse'})

        return int(race_number_tag.find('a').text)

    @staticmethod
    def _find_next_cursor(page_soup) -> str:
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

    @staticmethod
    def _parse_date(date_str: str) -> date:
        if date_str == 'today':
            return date.today()

        return parse(date_str).date()

    @staticmethod
    def _load_page_text(url: str) -> str:
        response = requests.get(url)

        if response.status_code == 429:
            raise ServerTooManyRequestsError(f"Couldn't load the page.")

        if not response.ok:
            raise RuntimeError("Something went wrong during page loading...")

        return response.text
