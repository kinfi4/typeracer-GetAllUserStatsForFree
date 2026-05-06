from typing import Iterator

import requests
from bs4 import BeautifulSoup

from src.constants import EXPORT_URL, TYPERACER_BASE_URL


class ExportFetcher:
    def __init__(self, session: requests.Session):
        self._session = session

    def fetch_all_buckets(self, username: str) -> Iterator[bytes]:
        bucket_paths = self._get_bucket_paths()
        total = len(bucket_paths)

        for i, path in enumerate(bucket_paths, 1):
            print(f'[Export]: Downloading bucket {i}/{total}...\r', flush=True, end='')
            response = self._session.get(f'{TYPERACER_BASE_URL}{path}')
            response.raise_for_status()
            yield response.content

        print()

    def _get_bucket_paths(self) -> list:
        response = self._session.get(f'{EXPORT_URL}?universe=play')
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return [
            a['href']
            for a in soup.find_all('a', href=True)
            if 'bucket=' in a['href']
        ]
