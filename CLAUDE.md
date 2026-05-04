# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

A CLI tool that scrapes race statistics from TypeRacer (typeracer.com) and generates visualizations. Users can fetch data fresh from the API or re-analyze a previously saved CSV file.

## Running the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Fetch stats for a username and display plots
python get_stats.py -u <username>

# With date range (DD-MM-YYYY format)
python get_stats.py -u <username> --start-date "01-01-2024" --end-date "31-12-2024"

# Save to a specific CSV file
python get_stats.py -u <username> -f output.csv

# Visualize from an existing CSV (no network requests)
python get_stats.py -n -f output.csv

# Fetch without showing plots
python get_stats.py -u <username> --hide-plots
```

There are no tests or linting configuration in this project.

## Architecture

Data flows linearly: `get_stats.py` (CLI) → `src/actions.py` (public API) → `src/parser.py` (scraping) → `src/statistics_analysis.py` (visualization/export).

**`get_stats.py`** — Entry point. Parses CLI args with `argparse`, validates dates, then calls either `actions.parse()` or `actions.plot_stats_from_file()`.

**`src/actions.py`** — Thin wrapper exposing two public functions used by `get_stats.py`. Instantiates `Parser` and `StatisticsVisualizer`.

**`src/parser.py`** — Core scraper. `Parser.parse_user_stats()` paginates the TypeRacer API (100 races per page, cursor-based), parses HTML with BeautifulSoup, and applies date-range filtering with early exit when `start_date` is reached. Returns a `StatisticsVisualizer` instance populated with a pandas DataFrame (`race`, `speed`, `accuracy`, `points`, `place`, `date` columns).

**`src/statistics_analysis.py`** — `StatisticsVisualizer` handles both CSV I/O (`save_to_file`, `get_stats_from_csv`) and all matplotlib plots: activity histogram, placement bar chart, WPM scatter plot, moving average, and rolling 10-race average. Uses PyQt5 as the matplotlib backend.

**`src/retry_decorator.py`** — `@retry()` decorator with exponential backoff (`2^n + random(0,2)` seconds) for handling HTTP 429 rate-limit responses from TypeRacer. Default max 4 retries.

**`src/constants.py`** — Holds the single TypeRacer API URL template.

**`src/exceptions.py`** — Defines `ServerTooManyRequestsError` raised on HTTP 429.

## Code Style

Write comments or docstrings only when the code is genuinely complex and a reader would be confused without them. Default to clean, comment-free code.

## Key Technical Details

- **Pagination**: Cursor extracted from the "load older" link in each page's HTML. Early exit optimization stops fetching once `start_date` is reached.
- **Date parsing**: Handles relative strings like `"today"` and absolute dates via `dateutil.parser.parse()`. Start date is inclusive, end date is exclusive.
- **Deprecated API**: `df.append()` in `parser.py` is removed in pandas ≥ 2.0 and must be replaced with `pd.concat()` if upgrading pandas.
- **HTML parsing**: Targets CSS classes `Scores__Table__Row`, `profileTableHeaderDate` in TypeRacer's DOM — if their frontend changes, the scraper will break silently.
