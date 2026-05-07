import sys
import subprocess
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

from src.auth import create_session, has_credentials
from src.constants import SCHEMA_COLUMNS
from src.fetchers.export_fetcher import ExportFetcher
from src.fetchers.html_fetcher import HtmlFetcher
from src.parsers.export_parser import ExportParser
from src.parsers.html_parser import HtmlParser


def parse(
    username: str,
    output_file: str,
    show_report: bool = True,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> None:
    session = create_session()

    if has_credentials():
        df = _fetch_via_export(session, username)
    else:
        df = _fetch_via_html(session, username, start_date)

    df = _filter_by_dates(df, start_date, end_date)
    _save_csv(df, output_file)

    if show_report:
        _launch_report(output_file)


def show_report_from_file(filepath: str) -> None:
    _launch_report(filepath)


def _fetch_via_export(session, username: str) -> pd.DataFrame:
    fetcher = ExportFetcher(session)
    parser = ExportParser()
    frames = [parser.parse_zip(zip_bytes) for zip_bytes in fetcher.fetch_all_buckets(username)]
    if not frames:
        return pd.DataFrame(columns=SCHEMA_COLUMNS)
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
        return pd.DataFrame(columns=SCHEMA_COLUMNS)
    return pd.DataFrame(rows)


def _filter_by_dates(df: pd.DataFrame, start_date: Optional[date], end_date: Optional[date]) -> pd.DataFrame:
    if start_date:
        df = df[df['date'] > start_date]
    if end_date:
        df = df[df['date'] <= end_date]
    return df


def _save_csv(df: pd.DataFrame, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def _launch_report(csv_path: str) -> None:
    script = Path(__file__).resolve().parent / 'report' / 'app.py'
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', str(script), '--', str(csv_path)])
