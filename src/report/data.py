from datetime import date, datetime
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st


_NUMERIC = ['race', 'speed', 'accuracy', 'points', 'text_id']
_EXTENDED = ['datetime', 'mode', 'text_id', 'skill_level', 'universe']


@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    for col in _EXTENDED:
        if col not in df.columns:
            df[col] = pd.NA

    for col in _NUMERIC:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=['speed', 'race']).copy()
    df['race'] = df['race'].astype(int)
    df['speed'] = df['speed'].astype(int)

    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce', utc=True)

    if df['datetime'].isna().all():
        df['datetime'] = pd.to_datetime(df['date'], errors='coerce', utc=True)

    place_split = df['place'].astype(str).str.split('/', n=1, expand=True)
    df['place_rank'] = pd.to_numeric(place_split[0], errors='coerce')
    df['place_total'] = pd.to_numeric(place_split[1], errors='coerce')
    df['is_win'] = df['place_rank'] == 1
    df['is_podium'] = df['place_rank'].isin([1, 2, 3])

    for col in ['mode', 'skill_level', 'universe']:
        if col in df.columns:
            df[col] = df[col].astype('string').replace({'nan': pd.NA, 'None': pd.NA, '': pd.NA})

    df = df.sort_values('race').reset_index(drop=True)
    return df


def has_extended_data(df: pd.DataFrame, column: str) -> bool:
    if column not in df.columns:
        return False
    return df[column].notna().any()


def has_hour_data(df: pd.DataFrame) -> bool:
    if 'datetime' not in df.columns:
        return False
    if df['datetime'].isna().all():
        return False
    hours = df['datetime'].dt.hour
    return hours.nunique(dropna=True) > 1


def filter_df(
    df: pd.DataFrame,
    start_date: Optional[date],
    end_date: Optional[date],
    wpm_range: Optional[tuple[int, int]] = None,
    accuracy_range: Optional[tuple[float, float]] = None,
    race_sizes: Optional[list[int]] = None,
    modes: Optional[list[str]] = None,
) -> pd.DataFrame:
    out = df

    if start_date is not None:
        out = out[out['date'] >= start_date]
    if end_date is not None:
        out = out[out['date'] <= end_date]

    if wpm_range is not None:
        lo, hi = wpm_range
        out = out[(out['speed'] >= lo) & (out['speed'] <= hi)]

    if accuracy_range is not None:
        lo, hi = accuracy_range
        out = out[(out['accuracy'].fillna(0) >= lo) & (out['accuracy'].fillna(100) <= hi)]

    if race_sizes:
        out = out[out['place_total'].isin(race_sizes)]

    if modes and has_extended_data(df, 'mode'):
        out = out[out['mode'].isin(modes)]

    return out.reset_index(drop=True)


def date_bounds(df: pd.DataFrame) -> tuple[date, date]:
    return df['date'].min(), df['date'].max()


def wpm_bounds(df: pd.DataFrame) -> tuple[int, int]:
    return int(df['speed'].min()), int(df['speed'].max())


def accuracy_bounds(df: pd.DataFrame) -> tuple[float, float]:
    if df['accuracy'].notna().any():
        return float(df['accuracy'].min()), float(df['accuracy'].max())
    return 0.0, 100.0


def available_race_sizes(df: pd.DataFrame) -> list[int]:
    sizes = df['place_total'].dropna().astype(int).unique().tolist()
    return sorted(sizes)


def available_modes(df: pd.DataFrame) -> list[str]:
    if not has_extended_data(df, 'mode'):
        return []
    return sorted(df['mode'].dropna().unique().tolist())
