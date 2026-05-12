"""포지션 콜백"""

from __future__ import annotations

import requests
from dash import Input, Output, callback
from dash.exceptions import PreventUpdate

from hdesk.dashboard.app import app

API_BASE = "http://localhost:8000/api/v1"


@app.callback(
    Output("overview-position-table", "data"),
    Input("interval-positions", "n_intervals"),
    prevent_initial_call=False,
)
def update_position_table(_n: int):
    """포지션 테이블 갱신."""
    try:
        resp = requests.get(f"{API_BASE}/positions", timeout=5)
        if resp.ok:
            return resp.json()
    except Exception:
        pass
    return []


@app.callback(
    Output("overview-portfolio-greeks", "children"),
    Input("interval-greeks", "n_intervals"),
    prevent_initial_call=False,
)
def update_portfolio_summary(_n: int):
    """포트폴리오 Greeks 요약 업데이트."""
    import dash_bootstrap_components as dbc

    try:
        resp = requests.get(f"{API_BASE}/greeks/portfolio", timeout=5)
        if resp.ok:
            g = resp.json()
            return dbc.Table(
                [
                    dbc.thead(dbc.tr([dbc.th("Greeks"), dbc.th("값")])),
                    dbc.tbody(
                        [
                            dbc.tr([dbc.td("Net Delta"), dbc.td(f"{g['net_delta']:,.2f}")]),
                            dbc.tr([dbc.td("Net Gamma"), dbc.td(f"{g['net_gamma']:,.4f}")]),
                            dbc.tr([dbc.td("Net Vega"), dbc.td(f"{g['net_vega']:,.0f}")]),
                            dbc.tr([dbc.td("Net Theta"), dbc.td(f"{g['net_theta']:,.0f}")]),
                        ]
                    ),
                ],
                bordered=True,
                dark=True,
                hover=True,
                size="sm",
            )
    except Exception:
        pass
    return "데이터 로딩 중..."
