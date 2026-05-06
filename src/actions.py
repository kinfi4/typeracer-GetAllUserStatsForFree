from datetime import date
from typing import Optional

import pandas as pd

from src.auth import create_session, has_credentials
from src.fetchers.export_fetcher import ExportFetcher
from src.fetchers.html_fetcher import HtmlFetcher
from src.parsers.export_parser import ExportParser
from src.parsers.html_parser import HtmlParser
from src.statistics_analysis import StatisticsVisualizer

_COLUMNS = ['race', 'speed', 'accuracy', 'points', 'place', 'date']


def parse(
    username: str,
    output_file: str,
    show_plots: bool = True,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> None:
    session = create_session()

    if has_credentials():
        df = _fetch_via_export(session, username)
    else:
        df = _fetch_via_html(session, username, start_date)

    df = _filter_by_dates(df, start_date, end_date)
    stats = StatisticsVisualizer(df)
    stats.save_to_file(output_file)

    if show_plots:
        stats.plot_everything()


def plot_stats_from_file(filepath: str, start_date: Optional[date] = None, end_date: Optional[date] = None):
    stats = StatisticsVisualizer.get_stats_from_csv(filepath, start_date, end_date)
    stats.plot_everything()


def _fetch_via_export(session, username: str) -> pd.DataFrame:
    fetcher = ExportFetcher(session)
    parser = ExportParser()
    frames = [parser.parse_zip(zip_bytes) for zip_bytes in fetcher.fetch_all_buckets(username)]
    if not frames:
        return pd.DataFrame(columns=_COLUMNS)
    return pd.concat(frames, ignore_index=True)


def _fetch_via_html(session, username: str, start_date: Optional[date]) -> pd.DataFrame:
    fetcher = HtmlFetcher(session)
    parser = HtmlParser()
    rows = []

    for html_text in fetcher.fetch_pages(username):
        page_rows = parser.parse_page(html_text)
        rows.extend(page_rows)
        if start_date and page_rows and min(r['date'] for r in page_rows) < start_date:
            break

    if not rows:
        return pd.DataFrame(columns=_COLUMNS)
    return pd.DataFrame(rows, columns=_COLUMNS)


def _filter_by_dates(df: pd.DataFrame, start_date: Optional[date], end_date: Optional[date]) -> pd.DataFrame:
    if start_date:
        df = df[df['date'] > start_date]
    if end_date:
        df = df[df['date'] <= end_date]
    return df
