# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

A CLI tool that fetches race statistics from TypeRacer and generates visualizations. When credentials are provided it uses TypeRacer's official export endpoint (reliable, complete); otherwise it falls back to HTML scraping.

## Running the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill in credentials (optional but recommended)
cp .env.example .env

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

Two pipelines share the same canonical DataFrame schema defined in `constants.SCHEMA_COLUMNS`: `race`, `speed`, `accuracy`, `points`, `place`, `date`, `datetime`, `mode`, `text_id`, `skill_level`, `universe`. The last five (`EXTENDED_COLUMNS`) are only populated by the export pipeline; the HTML pipeline fills them with `pd.NA`.

**Authenticated (preferred)** — `ExportFetcher` downloads per-bucket ZIPs from `data.typeracer.com/pit/export_data?universe=play&bucket=N` (1000 races each), `ExportParser` unzips and maps all 11 columns.

**Unauthenticated (fallback)** — `HtmlFetcher` paginates `data.typeracer.com/pit/race_history` via cursor-based links, `HtmlParser` extracts rows from `Scores__Table__Row` divs (extended columns set to `pd.NA`).

`src/actions.py` is the orchestration layer: calls `create_session()`, checks `has_credentials()`, picks the right fetcher+parser pair, applies date filtering, then hands the DataFrame to `StatisticsVisualizer`.

### Module Map

- **`get_stats.py`** — CLI entry point (`argparse`), date validation, calls `actions.parse()` or `actions.plot_stats_from_file()`
- **`src/actions.py`** — picks pipeline, filters by date, saves CSV via `_save_csv`, launches Streamlit report via `_launch_report` (subprocess)
- **`src/auth.py`** — `create_session()` / `has_credentials()`: reads `TYPERACER_USERNAME` + `TYPERACER_PASSWORD` from `.env`, POSTs to `/pit/login`
- **`src/fetchers/html_fetcher.py`** — `HtmlFetcher.fetch_pages(username)` generator: handles cursor pagination, progress output, `@retry` for 429s
- **`src/fetchers/export_fetcher.py`** — `ExportFetcher.fetch_all_buckets(username)` generator: scrapes bucket hrefs from export page, yields raw ZIP bytes
- **`src/parsers/html_parser.py`** — `HtmlParser.parse_page(html)` → `List[dict]` with all 11 schema columns
- **`src/parsers/export_parser.py`** — `ExportParser.parse_zip(bytes)` → `pd.DataFrame`; maps `Race #→race`, `WPM→speed`, `Accuracy×100→accuracy`, `Rank/# Racers→place`, `Date/Time (UTC)→date+datetime`, plus `Mode`, `Text ID`, `Skill Level`, `Universe`
- **`src/retry_decorator.py`** — `@retry()` with exponential backoff (`2^n + random(0,2)` s), default 4 retries
- **`src/constants.py`** — `URL` (HTML scraper template), `EXPORT_URL`, `TYPERACER_BASE_URL`, `SCHEMA_COLUMNS`, `EXTENDED_COLUMNS`
- **`src/exceptions.py`** — `ServerTooManyRequestsError` (raised on HTTP 429)

### Report module (`src/report/`)

A Streamlit + Plotly interactive dashboard (not yet wired to a CLI entry point; run separately with `streamlit run`). Requires `streamlit` and `plotly` which are **not** in `requirements.txt` yet.

- **`src/report/data.py`** — `load_csv(path)` (`@st.cache_data`): reads CSV, coerces types, splits `place` into `place_rank`/`place_total`, adds `is_win`/`is_podium` booleans. `filter_df()` applies date, WPM, accuracy, race-size, and mode filters.
- **`src/report/metrics.py`** — pure-pandas analytics: `compute_kpis`, `compare_periods` (last 30 days vs previous 30), `compute_streaks`, `compute_milestones`, `compute_personal_bests`, `compute_monthly_summary`
- **`src/report/charts.py`** — Plotly figure factories (all accept a preprocessed DataFrame): WPM scatter + rolling avg, histogram, PB progression, box by month, trend regression, animated monthly histogram, calendar heatmap, hour polar, day-of-week bar, monthly volume, hour×day heatmap, placement distribution, accuracy vs WPM scatter, cumulative points, mode performance, text repeat analysis, win-rate rolling
- **`src/report/components.py`** — Streamlit HTML helper components: `kpi_card`, `render_kpi_row`, `section_header`, `empty_state`, `hero`
- **`src/report/theme.py`** — `COLORS` dict, `HEATMAP_SCALE`, `SEQUENCE`, `register_template()` (registers a dark Plotly template), `CSS` string injected via `st.markdown`

## Code Style

Write comments or docstrings only when the code is genuinely complex and a reader would be confused without them. Default to clean, comment-free code.

## Key Technical Details

- **Export buckets**: each bucket URL (`?bucket=N`) returns a ZIP containing one CSV. Bucket links are scraped from the export page HTML — not hardcoded.
- **Column mapping (export CSV → DataFrame)**: `Accuracy` is a 0–1 float → stored as `str(round(val*100, 2))`. `place` combines `Rank` and `# Racers` as `"Rank/# Racers"` to stay compatible with `plot_places` which filters for `/5`. Extended columns (`datetime`, `mode`, `text_id`, `skill_level`, `universe`) are only populated by the export pipeline; charts/metrics that use them guard with `has_extended_data()`.
- **Date filtering**: `start_date` is exclusive, `end_date` is inclusive (both applied in `actions._filter_by_dates` after the full DataFrame is built; HTML pipeline also has an early-exit optimization).
- **HTML scraping**: targets CSS classes `Scores__Table__Row`, `profileTableHeaderDate`, `profileTableHeaderRaces` — fragile if TypeRacer changes their frontend.
- **Plot x-axis**: all plots use actual race numbers except `plot_mean_tens` which uses sequential index positions (1→N). Both correctly show oldest on the left because the DataFrame is sorted ascending by `race` before plotting.
- **`plot_places`**: only counts 5-player races (`str.contains('/5')`), an intentional filter in the original code.
