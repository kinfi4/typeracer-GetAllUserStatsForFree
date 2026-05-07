import plotly.graph_objects as go
import plotly.io as pio


COLORS = {
    'primary': '#22d3ee',
    'primary_soft': '#0891b2',
    'accent': '#f472b6',
    'accent_soft': '#be185d',
    'success': '#34d399',
    'warning': '#fbbf24',
    'danger': '#f87171',
    'gold': '#fcd34d',
    'silver': '#cbd5e1',
    'bronze': '#d97706',
    'muted': '#94a3b8',
    'bg': '#0f172a',
    'surface': '#1e293b',
    'border': '#334155',
    'text': '#e2e8f0',
}

SEQUENCE = [
    COLORS['primary'],
    COLORS['accent'],
    COLORS['success'],
    COLORS['warning'],
    COLORS['danger'],
    COLORS['gold'],
    COLORS['muted'],
]

HEATMAP_SCALE = [
    [0.0, '#0f172a'],
    [0.15, '#155e75'],
    [0.4, '#0891b2'],
    [0.7, '#22d3ee'],
    [1.0, '#a5f3fc'],
]


def register_template() -> str:
    template = go.layout.Template()
    template.layout.update(
        font=dict(family='Inter, system-ui, sans-serif', color=COLORS['text'], size=13),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        colorway=SEQUENCE,
        xaxis=dict(
            gridcolor=COLORS['border'],
            zerolinecolor=COLORS['border'],
            linecolor=COLORS['border'],
            tickfont=dict(color=COLORS['muted']),
        ),
        yaxis=dict(
            gridcolor=COLORS['border'],
            zerolinecolor=COLORS['border'],
            linecolor=COLORS['border'],
            tickfont=dict(color=COLORS['muted']),
        ),
        legend=dict(
            bgcolor='rgba(30,41,59,0.6)',
            bordercolor=COLORS['border'],
            borderwidth=1,
        ),
        hoverlabel=dict(
            bgcolor=COLORS['surface'],
            bordercolor=COLORS['primary'],
            font=dict(color=COLORS['text']),
        ),
        margin=dict(l=40, r=20, t=50, b=40),
        title=dict(font=dict(size=16, color=COLORS['text'])),
    )
    pio.templates['typeracer'] = template
    pio.templates.default = 'typeracer'
    return 'typeracer'


CSS = f"""
<style>
    .stApp {{
        background: linear-gradient(180deg, {COLORS['bg']} 0%, #0a0f1d 100%);
    }}
    section[data-testid="stSidebar"] {{
        background: {COLORS['surface']};
        border-right: 1px solid {COLORS['border']};
    }}
    .hero {{
        background: linear-gradient(135deg, rgba(34,211,238,0.12), rgba(244,114,182,0.10));
        border: 1px solid {COLORS['border']};
        border-radius: 18px;
        padding: 24px 28px;
        margin-bottom: 18px;
    }}
    .hero h1 {{
        margin: 0 0 4px 0;
        font-size: 30px;
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['accent']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .hero .meta {{ color: {COLORS['muted']}; font-size: 14px; }}
    .kpi {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 14px;
        padding: 16px 18px;
        height: 100%;
        position: relative;
        overflow: hidden;
    }}
    .kpi::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['accent']});
    }}
    .kpi .label {{
        color: {COLORS['muted']};
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 6px;
    }}
    .kpi .value {{
        color: {COLORS['text']};
        font-size: 28px;
        font-weight: 700;
        line-height: 1.1;
    }}
    .kpi .delta {{
        font-size: 12px;
        margin-top: 4px;
        display: inline-block;
    }}
    .kpi .delta.up {{ color: {COLORS['success']}; }}
    .kpi .delta.down {{ color: {COLORS['danger']}; }}
    .kpi .delta.flat {{ color: {COLORS['muted']}; }}
    .kpi .icon {{
        position: absolute;
        right: 14px;
        top: 18px;
        font-size: 22px;
        opacity: 0.45;
    }}
    .section-header {{
        margin: 18px 0 10px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid {COLORS['border']};
    }}
    .section-header h3 {{
        margin: 0;
        color: {COLORS['text']};
        font-size: 18px;
    }}
    .section-header .sub {{
        color: {COLORS['muted']};
        font-size: 13px;
        margin-top: 2px;
    }}
    .empty-state {{
        background: {COLORS['surface']};
        border: 1px dashed {COLORS['border']};
        border-radius: 12px;
        padding: 22px;
        text-align: center;
        color: {COLORS['muted']};
        font-size: 13px;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: {COLORS['surface']};
        border-radius: 10px 10px 0 0;
        padding: 8px 14px;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(180deg, rgba(34,211,238,0.18), {COLORS['surface']});
        border-bottom: 2px solid {COLORS['primary']};
    }}
</style>
"""
