from datetime import date
from typing import List

import pandas as pd
from bs4 import BeautifulSoup
from dateutil.parser import parse


class HtmlParser:
    def parse_page(self, html_text: str) -> List[dict]:
        soup = BeautifulSoup(html_text, 'html.parser')
        data_rows = soup.find_all('div', {'class': 'Scores__Table__Row'})

        rows = []
        for row in data_rows:
            date_str = row.find('div', {'class': 'profileTableHeaderDate'}).get_text(strip=True)
            race_cells = row.find_all('div', {'class': 'profileTableHeaderRaces'})

            rows.append({
                'race': row.find('div', {'class': 'profileTableHeaderUniverse'}).find('a').get_text(strip=True),
                'speed': race_cells[1].get_text(strip=True).replace(' WPM', ''),
                'accuracy': race_cells[2].get_text(strip=True).replace('%', ''),
                'points': row.find('div', {'class': 'profileTableHeaderAvg'}).get_text(strip=True),
                'place': row.find('div', {'class': 'profileTableHeaderPoints'}).get_text(strip=True),
                'date': self._parse_date(date_str),
                'datetime': pd.NA,
                'mode': pd.NA,
                'text_id': pd.NA,
                'skill_level': pd.NA,
                'universe': pd.NA,
            })

        return rows

    @staticmethod
    def _parse_date(date_str: str) -> date:
        if date_str == 'today':
            return date.today()
        return parse(date_str).date()
