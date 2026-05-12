"""Greeks 콜백 - 탭 전환, 히트맵 업데이트"""

from __future__ import annotations

import requests
from dash import Input, Output, callback
from dash.exceptions import PreventUpdate

from hdesk.dashboard.app import app
from hdesk.dashboard.components.greeks_heatmap import create_greeks_heatmap
from hdesk.dashboard.pages import greeks_monitor, overview, risk_report, vol_surface

API_BASE = "http://localhost:8000/api/v1"


@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab"),
)
def render_tab(active_tab: str):
    """활성 탭에 따라 페이지 레이아웃 렌더링."""
    if active_tab == "overview":
        return overview.layout()
    elif active_tab == "greeks":
        return greeks_monitor.layout()
    elif active_tab == "vol-surface":
        return vol_surface.layout()
    elif active_tab == "risk":
        return risk_report.layout()
    raise PreventUpdate


@app.callback(
    Output("greeks-heatmap", "figure"),
    Input("greeks-metric-selector", "value"),
    Input("greeks-underlying-selector", "value"),
    Input("interval-greeks", "n_intervals"),
    prevent_initial_call=True,
)
def update_greeks_heatmap(metric: str, underlying: str, _n: int):
    """Greeks 히트맵 갱신."""
    import pandas as pd
    import numpy as np

    # API에서 포지션 조회 후 Greeks 계산
    try:
        resp = requests.get(f"{API_BASE}/positions", timeout=3)
        positions = resp.json() if resp.ok else []
    except Exception:
        positions = []

    if not positions:
        import plotly.graph_objects as go

        return go.Figure().update_layout(
            title="데이터 없음", paper_bgcolor="#1a1a2e", font_color="white"
        )

    rows = []
    for pos in positions:
        if pos.get("instrument_type") != "OPTION":
            continue
        try:
            g_resp = requests.get(f"{API_BASE}/greeks/positions/{pos['id']}", timeout=3)
            if g_resp.ok:
                g = g_resp.json()
                rows.append({
                    "strike": pos["strike"],
                    "expiry": pos["expiry"],
                    metric: g.get(metric, 0.0),
                })
        except Exception:
            pass

    if not rows:
        import plotly.graph_objects as go

        return go.Figure().update_layout(title="옵션 포지션 없음", paper_bgcolor="#1a1a2e")

    df = pd.DataFrame(rows)
    return create_greeks_heatmap(df, metric=metric)
