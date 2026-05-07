# Get User Stats for TypeRacer

A CLI tool that fetches your TypeRacer race history and opens an interactive Streamlit dashboard with Plotly charts. When credentials are provided it uses TypeRacer's official export endpoint (full data); otherwise it falls back to HTML scraping (slightly narrower data — some charts gracefully degrade).

---

## Setup

```bash
git clone https://github.com/kinfi4/typeracer-GetAllUserStatsForFree.git
cd typeracer-GetAllUserStatsForFree
pip install -r requirements.txt
```

### Authentication (optional but recommended)

```bash
cp .env.example .env
# edit .env — set TYPERACER_USERNAME and TYPERACER_PASSWORD
```

Without credentials the script scrapes public HTML. With credentials it uses the official export endpoint, which provides extra fields (time of day, text ID, game mode, skill level) that unlock additional charts.

---

## Usage

```bash
# Fetch stats and open the interactive report in the browser
python get_stats.py -u <username>

# With a date range (DD-MM-YYYY)
python get_stats.py -u <username> --start-date "01-01-2024" --end-date "31-12-2024"

# Save to a specific CSV file
python get_stats.py -u <username> -f output.csv

# Fetch without launching the report (headless / CI)
python get_stats.py -u <username> --no-report

# Open the report from an existing CSV (no network requests)
python get_stats.py -n -f data/username-stats.csv
```

---

## Report

The dashboard opens at `http://localhost:8501` and includes:

| Tab | Contents |
|-----|----------|
| 📊 Overview | KPI cards (races, avg/max/median WPM, win rate, accuracy), 90-day sparkline |
| 🚀 Speed | WPM scatter + rolling avg, histogram, PB progression, monthly box plot, trend regression |
| 📅 Activity | Calendar heatmap, day-of-week bar, monthly volume, hour-of-day polar, hour×day heatmap |
| 🏆 Performance | Win/podium rate over time, placement distribution, accuracy vs WPM, cumulative points |
| 💎 Records | Top-10 tables, WPM milestones, mode breakdown, most-raced texts |
| 🎬 Animations | Animated monthly WPM distribution histogram |
| 🔍 Explorer | Filterable data table + CSV download |

The sidebar offers date presets (7d / 30d / 90d / YTD / 1y / all / custom), WPM range, accuracy range, race-size multi-select, and mode filter. All charts update live as you adjust filters.

---

## Arguments

| Flag | Description |
|------|-------------|
| `-u` / `--username` | TypeRacer username to fetch |
| `-f` / `--filename` | CSV path to save to (default: `data/<username>-stats.csv`) or load from (with `-n`) |
| `-n` / `--no-parsing` | Skip fetching — open report from an existing CSV (`-f` required) |
| `--start-date` | Earliest date to include, `DD-MM-YYYY` |
| `--end-date` | Latest date to include, `DD-MM-YYYY` |
| `--no-report` | Save CSV only, do not launch Streamlit |
