import calendar

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.report.theme import COLORS, HEATMAP_SCALE, SEQUENCE


_DAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def wpm_over_time(df: pd.DataFrame, rolling_window: int = 50) -> go.Figure:
    rolling = df['speed'].rolling(window=rolling_window, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=df['race'], y=df['speed'],
        mode='markers',
        marker=dict(size=3, color=COLORS['primary'], opacity=0.35),
        name='Race WPM',
        hovertemplate='Race %{x}<br>%{y} WPM<extra></extra>',
    ))
    fig.add_trace(go.Scatter(
        x=df['race'], y=rolling,
        mode='lines',
        line=dict(color=COLORS['accent'], width=2.5),
        name=f'Rolling avg ({rolling_window})',
        hovertemplate='Race %{x}<br>%{y:.1f} WPM<extra></extra>',
    ))
    fig.update_layout(
        xaxis_title='Race #', yaxis_title='WPM',
        height=420,
        margin=dict(t=10),
        legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01),
    )
    return fig


def wpm_histogram(df: pd.DataFrame) -> go.Figure:
    speeds = df['speed']
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=speeds,
        marker=dict(color=COLORS['primary'], line=dict(color=COLORS['border'], width=1)),
        nbinsx=60,
        name='Races',
    ))
    fig.update_layout(
        xaxis_title='WPM', yaxis_title='Races',
        height=380,
        showlegend=False,
        margin=dict(t=10),
    )
    return fig


def wpm_pb_progression(df: pd.DataFrame) -> go.Figure:
    pb = df['speed'].cummax()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['race'], y=pb,
        mode='lines',
        line=dict(color=COLORS['gold'], width=3, shape='hv'),
        fill='tozeroy', fillcolor='rgba(252,211,77,0.10)',
        name='Personal best',
        hovertemplate='Race %{x}<br>PB %{y} WPM<extra></extra>',
    ))
    fig.update_layout(
        xaxis_title='Race #', yaxis_title='Best WPM so far',
        height=380, showlegend=False,
        margin=dict(t=10),
    )
    return fig


def wpm_box_by_month(df: pd.DataFrame) -> go.Figure:
    work = df.copy()
    work['month'] = pd.to_datetime(work['date']).dt.to_period('M').dt.strftime('%Y-%m')
    fig = go.Figure(go.Box(
        x=work['month'],
        y=work['speed'],
        marker_color=COLORS['primary'],
        line_color=COLORS['primary'],
        showlegend=False,
        boxpoints=False,
    ))
    fig.update_layout(
        xaxis_title='Month', yaxis_title='WPM',
        height=400, showlegend=False,
        margin=dict(t=10),
    )
    return fig


def wpm_trend_regression(df: pd.DataFrame) -> go.Figure:
    if len(df) < 2:
        return _placeholder('Not enough data for trend')
    x = df['race'].astype(float).values
    y = df['speed'].astype(float).values
    slope, intercept = np.polyfit(x, y, 1)
    fit = slope * x + intercept

    work = df.copy()
    work['month'] = pd.to_datetime(work['date']).dt.to_period('M').dt.to_timestamp()
    races_per_month = work.groupby('month').size().mean() if work['month'].notna().any() else 0
    wpm_per_month = slope * races_per_month if races_per_month else 0

    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=df['race'], y=df['speed'],
        mode='markers',
        marker=dict(size=3, color=COLORS['primary'], opacity=0.3),
        name='Races',
    ))
    fig.add_trace(go.Scatter(
        x=df['race'], y=fit,
        mode='lines', line=dict(color=COLORS['accent'], width=3),
        name=f'Trend: +{wpm_per_month:.2f} WPM/month',
    ))
    fig.update_layout(
        xaxis_title='Race #', yaxis_title='WPM',
        height=400,
        margin=dict(t=10),
        legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01),
    )
    return fig


def wpm_distribution_animated(df: pd.DataFrame) -> go.Figure:
    work = df.copy()
    work['month'] = pd.to_datetime(work['date']).dt.to_period('M').dt.strftime('%Y-%m')
    months = sorted(work['month'].dropna().unique())
    if len(months) < 2:
        return _placeholder('Need at least 2 months of data for animation')

    bin_edges = np.linspace(work['speed'].min() - 1, work['speed'].max() + 1, 41)

    frames = []
    for m in months:
        subset = work[work['month'] == m]['speed']
        counts, _ = np.histogram(subset, bins=bin_edges)
        frames.append(go.Frame(
            name=m,
            data=[go.Bar(
                x=(bin_edges[:-1] + bin_edges[1:]) / 2,
                y=counts,
                marker=dict(color=COLORS['primary'], line=dict(color=COLORS['border'], width=0.5)),
            )],
            layout=go.Layout(title=f'{m} ({len(subset)} races)'),
        ))

    initial = work[work['month'] == months[0]]['speed']
    counts0, _ = np.histogram(initial, bins=bin_edges)

    fig = go.Figure(
        data=[go.Bar(
            x=(bin_edges[:-1] + bin_edges[1:]) / 2,
            y=counts0,
            marker=dict(color=COLORS['primary'], line=dict(color=COLORS['border'], width=0.5)),
        )],
        frames=frames,
    )
    fig.update_layout(
        title=f'{months[0]} ({len(initial)} races)',
        xaxis_title='WPM', yaxis_title='Races',
        height=460,
        updatemenus=[dict(
            type='buttons',
            showactive=False,
            direction='right',
            x=0.05, y=-0.15, xanchor='left', yanchor='top',
            buttons=[
                dict(label='▶ Play', method='animate',
                     args=[None, dict(frame=dict(duration=400, redraw=True), fromcurrent=True, transition=dict(duration=200))]),
                dict(label='❚❚ Pause', method='animate',
                     args=[[None], dict(frame=dict(duration=0, redraw=False), mode='immediate', transition=dict(duration=0))]),
            ],
        )],
        sliders=[dict(
            active=0, x=0.15, y=-0.12, len=0.8,
            currentvalue=dict(prefix='Month: ', font=dict(color=COLORS['accent'])),
            steps=[dict(method='animate', label=m,
                        args=[[m], dict(frame=dict(duration=400, redraw=True), mode='immediate')]) for m in months],
        )],
        margin=dict(b=80),
    )
    return fig


def calendar_heatmap(df: pd.DataFrame) -> go.Figure:
    if len(df) == 0:
        return _placeholder('No activity to show')
    counts = df.groupby('date').size().rename('races').reset_index()
    start = pd.Timestamp(counts['date'].min())
    end = pd.Timestamp(counts['date'].max())
    start = start - pd.Timedelta(days=start.weekday())
    full = pd.DataFrame({'date': pd.date_range(start, end, freq='D')})
    full['date_only'] = full['date'].dt.date
    merged = full.merge(counts, left_on='date_only', right_on='date', how='left', suffixes=('', '_y'))
    merged['races'] = merged['races'].fillna(0)
    merged['weekday'] = merged['date'].dt.weekday
    merged['week'] = ((merged['date'] - start).dt.days) // 7

    pivot = merged.pivot_table(index='weekday', columns='week', values='races', aggfunc='sum').reindex(range(7))
    hover = merged.pivot_table(index='weekday', columns='week', values='date_only', aggfunc='first').reindex(range(7))

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        colorscale=HEATMAP_SCALE,
        showscale=True,
        xgap=2, ygap=2,
        customdata=hover.values,
        hovertemplate='%{customdata}<br>%{z:.0f} races<extra></extra>',
        colorbar=dict(title='Races', tickfont=dict(color=COLORS['muted'])),
    ))
    fig.update_layout(
        height=260,
        yaxis=dict(tickmode='array', tickvals=list(range(7)), ticktext=_DAY_LABELS, autorange='reversed'),
        xaxis=dict(showticklabels=False, title=''),
        margin=dict(l=50, r=20, t=10, b=20),
    )
    return fig


def hour_polar(df: pd.DataFrame) -> go.Figure:
    hours = df['datetime'].dt.hour
    counts = hours.value_counts().reindex(range(24), fill_value=0).sort_index()
    fig = go.Figure(go.Barpolar(
        r=counts.values,
        theta=[h * 15 for h in counts.index],
        marker=dict(
            color=counts.values,
            colorscale=HEATMAP_SCALE,
            line=dict(color=COLORS['border'], width=1),
        ),
        hovertemplate='%{theta}h<br>%{r} races<extra></extra>',
    ))
    fig.update_layout(
        height=420,
        margin=dict(t=10),
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(showticklabels=True, color=COLORS['muted'], gridcolor=COLORS['border']),
            angularaxis=dict(
                tickmode='array',
                tickvals=[h * 15 for h in range(24)],
                ticktext=[f'{h:02d}' for h in range(24)],
                direction='clockwise',
                rotation=90,
                color=COLORS['muted'],
                gridcolor=COLORS['border'],
            ),
        ),
    )
    return fig


def day_of_week_bar(df: pd.DataFrame) -> go.Figure:
    work = df.copy()
    work['weekday'] = pd.to_datetime(work['date']).dt.weekday
    counts = work.groupby('weekday').size().reindex(range(7), fill_value=0)
    avg_wpm = work.groupby('weekday')['speed'].mean().reindex(range(7), fill_value=0)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=_DAY_LABELS, y=counts.values,
        marker=dict(color=COLORS['primary']),
        name='Races',
        hovertemplate='%{x}<br>%{y} races<extra></extra>',
    ))
    fig.add_trace(go.Scatter(
        x=_DAY_LABELS, y=avg_wpm.values,
        mode='lines+markers',
        line=dict(color=COLORS['accent'], width=2),
        marker=dict(size=8, color=COLORS['accent']),
        name='Avg WPM',
        yaxis='y2',
        hovertemplate='%{x}<br>%{y:.1f} WPM<extra></extra>',
    ))
    fig.update_layout(
        xaxis_title='', yaxis_title='Races',
        yaxis2=dict(title='Avg WPM', overlaying='y', side='right',
                    showgrid=False, color=COLORS['accent']),
        height=360,
        margin=dict(t=10),
        legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01),
    )
    return fig


def monthly_volume_bar(df: pd.DataFrame) -> go.Figure:
    work = df.copy()
    work['month'] = pd.to_datetime(work['date']).dt.to_period('M').dt.to_timestamp()
    grouped = work.groupby('month').agg(races=('race', 'count'), avg_wpm=('speed', 'mean')).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped['month'], y=grouped['races'],
        marker=dict(
            color=grouped['avg_wpm'],
            colorscale=HEATMAP_SCALE,
            colorbar=dict(title='Avg WPM', tickfont=dict(color=COLORS['muted'])),
        ),
        hovertemplate='%{x|%b %Y}<br>%{y} races<br>Avg %{marker.color:.1f} WPM<extra></extra>',
    ))
    fig.update_layout(
        xaxis_title='', yaxis_title='Races',
        height=360, showlegend=False,
        margin=dict(t=10),
    )
    return fig


def hour_dow_heatmap(df: pd.DataFrame) -> go.Figure:
    work = df.copy()
    work['hour'] = work['datetime'].dt.hour
    work['weekday'] = work['datetime'].dt.weekday
    pivot = work.pivot_table(index='weekday', columns='hour', values='speed', aggfunc='mean')
    pivot = pivot.reindex(index=range(7), columns=range(24))
    counts = work.pivot_table(index='weekday', columns='hour', values='race', aggfunc='count')
    counts = counts.reindex(index=range(7), columns=range(24)).fillna(0)

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f'{h:02d}' for h in range(24)],
        y=_DAY_LABELS,
        colorscale=HEATMAP_SCALE,
        colorbar=dict(title='Avg WPM', tickfont=dict(color=COLORS['muted'])),
        customdata=counts.values,
        hovertemplate='%{y} %{x}h<br>%{z:.1f} avg WPM<br>%{customdata:.0f} races<extra></extra>',
    ))
    fig.update_layout(
        xaxis_title='Hour (UTC)', yaxis_title='',
        yaxis=dict(autorange='reversed'),
        height=360,
        margin=dict(t=10),
    )
    return fig


def place_distribution_by_size(df: pd.DataFrame) -> go.Figure:
    work = df.dropna(subset=['place_rank', 'place_total']).copy()
    if len(work) == 0:
        return _placeholder('No placement data')
    work['place_rank'] = work['place_rank'].astype(int)
    work['place_total'] = work['place_total'].astype(int)
    grouped = work.groupby(['place_total', 'place_rank']).size().reset_index(name='races')
    sizes = sorted(grouped['place_total'].unique())

    fig = go.Figure()
    for i, size in enumerate(sizes):
        subset = grouped[grouped['place_total'] == size]
        fig.add_trace(go.Bar(
            x=[f'{r}/{size}' for r in subset['place_rank']],
            y=subset['races'],
            name=f'{size}-player',
            marker=dict(color=SEQUENCE[i % len(SEQUENCE)]),
            hovertemplate='%{x}<br>%{y} races<extra></extra>',
        ))
    fig.update_layout(
        xaxis_title='Place', yaxis_title='Races',
        height=380, barmode='group',
        margin=dict(t=10),
        legend=dict(orientation='h', yanchor='top', y=0.99, xanchor='left', x=0.01),
    )
    return fig


def accuracy_vs_wpm_scatter(df: pd.DataFrame) -> go.Figure:
    work = df.dropna(subset=['accuracy']).copy()
    if len(work) == 0:
        return _placeholder('No accuracy data')
    corr = work['speed'].corr(work['accuracy'])
    fig = go.Figure(go.Scattergl(
        x=work['accuracy'], y=work['speed'],
        mode='markers',
        marker=dict(
            size=4,
            color=work['speed'],
            colorscale=HEATMAP_SCALE,
            opacity=0.5,
            colorbar=dict(title='WPM', tickfont=dict(color=COLORS['muted'])),
        ),
        hovertemplate='%{x:.1f}% accuracy<br>%{y} WPM<extra></extra>',
    ))
    fig.update_layout(
        title=f'r = {corr:.2f}',
        xaxis_title='Accuracy (%)', yaxis_title='WPM',
        height=400,
        margin=dict(t=30),
    )
    return fig


def points_cumulative(df: pd.DataFrame) -> go.Figure:
    work = df.dropna(subset=['points']).copy()
    if len(work) == 0:
        return _placeholder('No points data')
    work['cumulative'] = work['points'].cumsum()
    fig = go.Figure(go.Scatter(
        x=work['race'], y=work['cumulative'],
        mode='lines',
        line=dict(color=COLORS['gold'], width=2.5),
        fill='tozeroy', fillcolor='rgba(252,211,77,0.10)',
        hovertemplate='Race %{x}<br>%{y:,.0f} total points<extra></extra>',
    ))
    fig.update_layout(
        xaxis_title='Race #', yaxis_title='Points',
        height=360, showlegend=False,
        margin=dict(t=10),
    )
    return fig


def mode_performance_bar(df: pd.DataFrame) -> go.Figure:
    work = df.dropna(subset=['mode']).copy()
    if len(work) == 0:
        return _placeholder('No mode data — fetch via authenticated export to enable')
    grouped = work.groupby('mode').agg(races=('race', 'count'), avg_wpm=('speed', 'mean'),
                                       max_wpm=('speed', 'max')).reset_index().sort_values('races', ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped['mode'], y=grouped['avg_wpm'],
        marker=dict(color=COLORS['primary']),
        name='Avg WPM',
        text=[f'{v:.0f}' for v in grouped['avg_wpm']],
        textposition='outside',
        hovertemplate='%{x}<br>Avg %{y:.1f} WPM<br>'
                      'Max ' + grouped['max_wpm'].astype(str) + ' WPM<br>'
                      + grouped['races'].astype(str) + ' races<extra></extra>',
    ))
    fig.update_layout(
        xaxis_title='', yaxis_title='Avg WPM',
        height=360, showlegend=False,
        margin=dict(t=10),
    )
    return fig


def text_repeat_analysis(df: pd.DataFrame, n: int = 10) -> go.Figure:
    work = df.dropna(subset=['text_id']).copy()
    if len(work) == 0:
        return _placeholder('No text data — fetch via authenticated export to enable')
    grouped = work.groupby('text_id').agg(
        races=('race', 'count'),
        avg_wpm=('speed', 'mean'),
        first=('speed', 'first'),
        last=('speed', 'last'),
    ).reset_index().sort_values('races', ascending=False).head(n)
    grouped['delta'] = grouped['last'] - grouped['first']

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f'#{int(t)}' for t in grouped['text_id']],
        y=grouped['races'],
        marker=dict(color=grouped['avg_wpm'], colorscale=HEATMAP_SCALE,
                    colorbar=dict(title='Avg WPM', tickfont=dict(color=COLORS['muted']))),
        hovertemplate='Text #%{x}<br>%{y} races<br>'
                      'Avg %{marker.color:.1f} WPM<extra></extra>',
    ))
    fig.update_layout(
        xaxis_title='Text ID', yaxis_title='Races',
        height=380,
        margin=dict(t=10),
    )
    return fig


def wpm_sparkline(df: pd.DataFrame, days: int = 90) -> go.Figure:
    if len(df) == 0:
        return _placeholder('')
    work = df.copy()
    end = pd.to_datetime(work['date'].max())
    start = end - pd.Timedelta(days=days)
    work['date_dt'] = pd.to_datetime(work['date'])
    recent = work[work['date_dt'] >= start]
    if len(recent) == 0:
        recent = work.tail(min(len(work), 200))
    daily = recent.groupby(recent['date_dt'].dt.date)['speed'].mean()

    fig = go.Figure(go.Scatter(
        x=list(daily.index), y=daily.values,
        mode='lines',
        line=dict(color=COLORS['primary'], width=2.2),
        fill='tozeroy', fillcolor='rgba(34,211,238,0.08)',
        hovertemplate='%{x}<br>%{y:.1f} avg WPM<extra></extra>',
    ))
    fig.update_layout(
        height=140,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=True, color=COLORS['muted']),
        yaxis=dict(showgrid=False, showticklabels=False, range=[max(0, daily.min() - 5), daily.max() + 5]),
    )
    return fig


def win_rate_over_time(df: pd.DataFrame, window: int = 100) -> go.Figure:
    work = df.dropna(subset=['place_rank']).copy()
    if len(work) == 0:
        return _placeholder('No placement data')
    work['win_roll'] = work['is_win'].rolling(window=window, min_periods=10).mean() * 100
    work['podium_roll'] = work['is_podium'].rolling(window=window, min_periods=10).mean() * 100
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=work['race'], y=work['podium_roll'],
        mode='lines', line=dict(color=COLORS['silver'], width=2),
        name='Podium %', fill='tozeroy', fillcolor='rgba(203,213,225,0.06)',
    ))
    fig.add_trace(go.Scatter(
        x=work['race'], y=work['win_roll'],
        mode='lines', line=dict(color=COLORS['gold'], width=2.5),
        name='Win %',
    ))
    fig.update_layout(
        xaxis_title='Race #', yaxis_title='%',
        height=380,
        margin=dict(t=10),
        legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01),
    )
    return fig


def _placeholder(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message, x=0.5, y=0.5, xref='paper', yref='paper',
        showarrow=False, font=dict(color=COLORS['muted'], size=14),
    )
    fig.update_layout(
        height=300,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
    )
    return fig
