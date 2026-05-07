import sys
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.report.theme import CSS, register_template
from src.report.data import (
    load_csv, filter_df, has_extended_data, has_hour_data,
    date_bounds, wpm_bounds, accuracy_bounds,
)
from src.report.metrics import (
    compute_kpis, compare_periods, compute_streaks, compute_milestones, compute_personal_bests,
)
from src.report import charts
from src.report.components import hero, render_kpi_row, section_header, empty_state


def _csv_path() -> str:
    if len(sys.argv) < 2:
        st.error("Usage: streamlit run src/report/app.py -- <path_to_csv>")
        st.stop()
    return sys.argv[1]


def main() -> None:
    st.set_page_config(page_title="TypeRacer Stats", layout="wide", initial_sidebar_state="expanded")
    st.markdown(CSS, unsafe_allow_html=True)
    register_template()

    path = _csv_path()
    df_full = load_csv(path)

    if len(df_full) == 0:
        st.error("No data found in CSV.")
        st.stop()

    d_min, d_max = date_bounds(df_full)
    today = date.today()

    with st.sidebar:
        st.title("Filters")

        preset = st.radio("Date range", ["All", "7d", "30d", "90d", "Current Year", "1y", "Custom"], index=0)

        if preset == "All":
            start_date, end_date = d_min, d_max
        elif preset == "7d":
            start_date, end_date = today - timedelta(days=7), today
        elif preset == "30d":
            start_date, end_date = today - timedelta(days=30), today
        elif preset == "90d":
            start_date, end_date = today - timedelta(days=90), today
        elif preset == "Current Year":
            start_date, end_date = date(today.year, 1, 1), today
        elif preset == "1y":
            start_date, end_date = today - timedelta(days=365), today
        else:
            start_date = st.date_input("From", value=d_min, min_value=d_min, max_value=d_max)
            end_date = st.date_input("To", value=d_max, min_value=d_min, max_value=d_max)

        st.divider()

        w_min, w_max = wpm_bounds(df_full)
        wpm_range = st.slider("WPM range", w_min, w_max, (w_min, w_max))

        a_min, a_max = accuracy_bounds(df_full)
        accuracy_range = (
            st.slider("Accuracy range", float(a_min), float(a_max), (float(a_min), float(a_max)), step=0.5)
            if a_max > a_min else None
        )

        st.divider()
        if st.button("↻ Reset filters"):
            st.rerun()

    df = filter_df(
        df_full,
        start_date=start_date,
        end_date=end_date,
        wpm_range=wpm_range if wpm_range != (w_min, w_max) else None,
        accuracy_range=accuracy_range if accuracy_range and tuple(accuracy_range) != (float(a_min), float(a_max)) else None,
    )

    username = Path(path).stem.replace("-stats", "")
    date_range_str = f"{df['date'].min()} → {df['date'].max()}" if len(df) else "No data"
    hero(username, len(df), date_range_str)

    tab_labels = ["Overview", "Speed", "Activity", "Performance", "Records", "Animations", "Explorer"]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        _tab_overview(df)
    with tabs[1]:
        _tab_speed(df)
    with tabs[2]:
        _tab_activity(df)
    with tabs[3]:
        _tab_performance(df)
    with tabs[4]:
        _tab_records(df)
    with tabs[5]:
        _tab_animations(df)
    with tabs[6]:
        _tab_explorer(df)


def _tab_overview(df):
    if len(df) == 0:
        empty_state("No data matches the current filters.")
        return

    kpis = compute_kpis(df)
    comp = compare_periods(df)

    def _delta(cur, prev, fmt=".1f", unit=""):
        if not prev:
            return None, "flat"
        diff = cur - prev
        sign = "+" if diff >= 0 else ""
        direction = "up" if diff > 0 else ("down" if diff < 0 else "flat")
        return f"{sign}{diff:{fmt}}{unit}", direction

    wpm_delta, wpm_dir = _delta(comp.get("cur_avg_wpm", 0), comp.get("prev_avg_wpm", 0), unit=" WPM")
    races_delta, races_dir = _delta(comp.get("cur_races", 0), comp.get("prev_races", 0), fmt="d", unit=" races")

    render_kpi_row([
        dict(label="Total Races", value=f"{kpis['total_races']:,}", icon="🏁"),
        dict(label="Avg WPM", value=f"{kpis['avg_wpm']:.0f}", delta=wpm_delta, delta_dir=wpm_dir, icon="🚀"),
        dict(label="Max WPM", value=str(kpis["max_wpm"]), icon="⚡"),
        dict(label="Median WPM", value=f"{kpis['median_wpm']:.0f}", icon="📊"),
    ])
    render_kpi_row([
        dict(label="Win Rate", value=f"{kpis['win_rate']:.1f}%", icon="🏆"),
        dict(label="Podium Rate", value=f"{kpis['podium_rate']:.1f}%", icon="🥉"),
        dict(label="Avg Accuracy", value=f"{kpis['avg_accuracy']:.1f}%" if kpis["avg_accuracy"] else "N/A", icon="🎯"),
        dict(label="Active Days", value=str(kpis["active_days"]), icon="📅"),
    ])

    section_header("Recent activity (last 90 days)")
    st.plotly_chart(charts.wpm_sparkline(df), use_container_width=True)


def _tab_speed(df):
    if len(df) == 0:
        empty_state("No data.")
        return

    section_header("WPM Over Time")
    st.plotly_chart(charts.wpm_over_time(df), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        section_header("WPM Distribution")
        st.plotly_chart(charts.wpm_histogram(df), use_container_width=True)
    with col2:
        section_header("Personal Best Progression")
        st.plotly_chart(charts.wpm_pb_progression(df), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        section_header("WPM by Month")
        st.plotly_chart(charts.wpm_box_by_month(df), use_container_width=True)
    with col4:
        section_header("Speed Trend")
        st.plotly_chart(charts.wpm_trend_regression(df), use_container_width=True)


def _tab_activity(df):
    if len(df) == 0:
        empty_state("No data.")
        return

    streaks = compute_streaks(df)
    render_kpi_row([
        dict(label="Current streak", value=f"{streaks['current']}d", icon="🔥"),
        dict(label="Longest streak", value=f"{streaks['longest']}d", icon="🏅"),
        dict(label="Active days", value=str(streaks["active_days"]), icon="📅"),
    ])

    section_header("Activity Calendar")
    st.plotly_chart(charts.calendar_heatmap(df), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        section_header("Day of Week")
        st.plotly_chart(charts.day_of_week_bar(df), use_container_width=True)
    with col2:
        section_header("Monthly Volume")
        st.plotly_chart(charts.monthly_volume_bar(df), use_container_width=True)

    if has_hour_data(df):
        col3, col4 = st.columns(2)
        with col3:
            section_header("Races by Hour (UTC)")
            st.plotly_chart(charts.hour_polar(df), use_container_width=True)
        with col4:
            section_header("When You Race Fastest")
            st.plotly_chart(charts.hour_dow_heatmap(df), use_container_width=True)
    else:
        empty_state("Hour-of-day charts require authenticated export data (datetime column is missing or date-only).")


def _tab_performance(df):
    if len(df) == 0:
        empty_state("No data.")
        return

    section_header("Win & Podium Rate Over Time")
    st.plotly_chart(charts.win_rate_over_time(df), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        section_header("Placements by Race Size")
        st.plotly_chart(charts.place_distribution_by_size(df), use_container_width=True)
    with col2:
        section_header("Accuracy vs WPM Scatter")
        st.plotly_chart(charts.accuracy_vs_wpm_scatter(df), use_container_width=True)

    section_header("Cumulative Points")
    st.plotly_chart(charts.points_cumulative(df), use_container_width=True)


def _tab_records(df):
    if len(df) == 0:
        empty_state("No data.")
        return

    pbs = compute_personal_bests(df)
    col1, col2, col3 = st.columns(3)
    with col1:
        section_header("Top 10 Fastest")
        st.dataframe(pbs["fastest"], use_container_width=True)
    with col2:
        section_header("Top 10 Accuracy")
        st.dataframe(pbs["highest_accuracy"], use_container_width=True)
    with col3:
        section_header("Top 10 Points")
        st.dataframe(pbs["highest_points"], use_container_width=True)

    milestones = compute_milestones(df)
    if len(milestones) > 0:
        section_header("WPM Milestones")
        st.dataframe(milestones, use_container_width=True)

    if has_extended_data(df, "mode"):
        section_header("Performance by Mode")
        st.plotly_chart(charts.mode_performance_bar(df), use_container_width=True)
    else:
        empty_state("Mode breakdown requires authenticated export (mode column missing).")

    if has_extended_data(df, "text_id"):
        section_header("Most-Raced Texts")
        st.plotly_chart(charts.text_repeat_analysis(df), use_container_width=True)
    else:
        empty_state("Text repeat analysis requires authenticated export (text_id column missing).")


def _tab_animations(df):
    if len(df) == 0:
        empty_state("No data.")
        return

    section_header("WPM Distribution Over Time")
    st.plotly_chart(charts.wpm_distribution_animated(df), use_container_width=True)


def _tab_explorer(df):
    section_header("Data Explorer", subtitle=f"{len(df):,} races")
    st.dataframe(df, use_container_width=True)
    st.download_button(
        "⬇ Download CSV",
        data=df.to_csv(index=False).encode(),
        file_name="typeracer_stats_filtered.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
