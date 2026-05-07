from datetime import date, timedelta

import numpy as np
import pandas as pd


_MILESTONE_WPMS = [40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]


def compute_kpis(df: pd.DataFrame) -> dict:
    if len(df) == 0:
        return {
            'total_races': 0,
            'avg_wpm': 0.0,
            'median_wpm': 0.0,
            'max_wpm': 0,
            'win_rate': 0.0,
            'podium_rate': 0.0,
            'avg_accuracy': 0.0,
            'total_points': 0.0,
            'active_days': 0,
        }
    return {
        'total_races': len(df),
        'avg_wpm': float(df['speed'].mean()),
        'median_wpm': float(df['speed'].median()),
        'max_wpm': int(df['speed'].max()),
        'win_rate': float(df['is_win'].mean() * 100),
        'podium_rate': float(df['is_podium'].mean() * 100),
        'avg_accuracy': float(df['accuracy'].mean()) if df['accuracy'].notna().any() else 0.0,
        'total_points': float(df['points'].sum()) if df['points'].notna().any() else 0.0,
        'active_days': int(df['date'].nunique()),
    }


def compare_periods(df: pd.DataFrame, current_days: int = 30) -> dict:
    if len(df) == 0:
        return {}
    end = df['date'].max()
    cur_start = end - timedelta(days=current_days)
    prev_start = cur_start - timedelta(days=current_days)

    cur = df[(df['date'] > cur_start) & (df['date'] <= end)]
    prev = df[(df['date'] > prev_start) & (df['date'] <= cur_start)]

    def safe_mean(s):
        return float(s.mean()) if len(s) else 0.0

    return {
        'cur_races': len(cur),
        'prev_races': len(prev),
        'cur_avg_wpm': safe_mean(cur['speed']),
        'prev_avg_wpm': safe_mean(prev['speed']),
        'cur_max_wpm': int(cur['speed'].max()) if len(cur) else 0,
        'prev_max_wpm': int(prev['speed'].max()) if len(prev) else 0,
    }


def compute_streaks(df: pd.DataFrame) -> dict:
    if len(df) == 0:
        return {'current': 0, 'longest': 0, 'active_days': 0}

    days = sorted(df['date'].dropna().unique())
    if not days:
        return {'current': 0, 'longest': 0, 'active_days': 0}

    longest = current_run = 1
    for prev_day, day in zip(days, days[1:]):
        if (day - prev_day).days == 1:
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 1

    today = date.today()
    last_day = days[-1]
    days_set = set(days)
    if (today - last_day).days > 1:
        current = 0
    else:
        current = 1
        d = last_day
        while (d - timedelta(days=1)) in days_set:
            d -= timedelta(days=1)
            current += 1

    return {'current': current, 'longest': longest, 'active_days': len(days)}


def compute_milestones(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) == 0:
        return pd.DataFrame(columns=['wpm', 'race', 'date'])
    rows = []
    for threshold in _MILESTONE_WPMS:
        hit = df[df['speed'] >= threshold]
        if len(hit) > 0:
            first = hit.iloc[0]
            rows.append({
                'wpm': threshold,
                'race': int(first['race']),
                'date': first['date'],
            })
    return pd.DataFrame(rows)


def compute_personal_bests(df: pd.DataFrame, n: int = 10) -> dict:
    if len(df) == 0:
        empty = pd.DataFrame(columns=['race', 'speed', 'accuracy', 'points', 'date'])
        return {'fastest': empty, 'highest_accuracy': empty, 'highest_points': empty}
    cols = ['race', 'speed', 'accuracy', 'points', 'date']
    return {
        'fastest': df.nlargest(n, 'speed')[cols].reset_index(drop=True),
        'highest_accuracy': df.nlargest(n, 'accuracy')[cols].reset_index(drop=True),
        'highest_points': df.nlargest(n, 'points')[cols].reset_index(drop=True),
    }


def compute_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) == 0:
        return pd.DataFrame(columns=['month', 'races', 'avg_wpm', 'max_wpm'])
    work = df.copy()
    work['month'] = pd.to_datetime(work['date']).dt.to_period('M').dt.to_timestamp()
    grouped = work.groupby('month').agg(
        races=('race', 'count'),
        avg_wpm=('speed', 'mean'),
        max_wpm=('speed', 'max'),
        avg_accuracy=('accuracy', 'mean'),
        win_rate=('is_win', 'mean'),
    ).reset_index()
    grouped['win_rate'] *= 100
    return grouped


def rolling_avg(df: pd.DataFrame, window: int) -> pd.Series:
    return df['speed'].rolling(window=window, min_periods=1).mean()


def running_max(df: pd.DataFrame) -> pd.Series:
    return df['speed'].cummax()


def calendar_matrix(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) == 0:
        return pd.DataFrame()
    counts = df.groupby('date').size().rename('races').reset_index()
    start = counts['date'].min()
    end = counts['date'].max()
    full = pd.DataFrame({'date': pd.date_range(start, end, freq='D').date})
    merged = full.merge(counts, on='date', how='left').fillna({'races': 0})
    merged['date'] = pd.to_datetime(merged['date'])
    merged['weekday'] = merged['date'].dt.weekday
    merged['week'] = (merged['date'] - merged['date'].min()).dt.days // 7
    return merged


def newest_pb(df: pd.DataFrame) -> dict:
    if len(df) == 0:
        return {}
    idx = df['speed'].idxmax()
    row = df.loc[idx]
    return {
        'wpm': int(row['speed']),
        'race': int(row['race']),
        'date': row['date'],
    }
