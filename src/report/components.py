from typing import Optional

import streamlit as st


def kpi_card(label: str, value: str, delta: Optional[str] = None, delta_dir: str = 'flat', icon: str = '') -> str:
    delta_html = ''
    if delta:
        delta_html = f'<div class="delta {delta_dir}">{delta}</div>'
    icon_html = f'<div class="icon">{icon}</div>' if icon else ''
    return f"""
    <div class="kpi">
        {icon_html}
        <div class="label">{label}</div>
        <div class="value">{value}</div>
        {delta_html}
    </div>
    """


def render_kpi_row(cards: list[dict]) -> None:
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        with col:
            st.markdown(kpi_card(**card), unsafe_allow_html=True)


def section_header(title: str, subtitle: Optional[str] = None) -> None:
    sub_html = f'<div class="sub">{subtitle}</div>' if subtitle else ''
    st.markdown(
        f'<div class="section-header"><h3>{title}</h3>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def empty_state(message: str) -> None:
    st.markdown(f'<div class="empty-state">{message}</div>', unsafe_allow_html=True)


def hero(username: str, total_races: int, date_range: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1>{username}</h1>
            <div class="meta">{total_races:,} races · {date_range}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
