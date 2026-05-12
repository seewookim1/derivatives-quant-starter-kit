"""리스크 콜백"""

from __future__ import annotations

import requests
from dash import Input, Output
from dash.exceptions import PreventUpdate

from hdesk.dashboard.app import app
from hdesk.dashboard.components.risk_gauge import create_risk_gauge

API_BASE = "http://localhost:8000/api/v1"


@app.callback(
    Output("overview-limits", "children"),
    Input("interval-risk", "n_intervals"),
    prevent_initial_call=False,
)
def update_limits_display(_n: int):
    """리스크 한도 게이지 갱신."""
    from dash import dcc

    try:
        resp = requests.get(f"{API_BASE}/risk/limits", timeout=5)
        if resp.ok:
            events = resp.json()
            gauges = []
            for event in events:
                fig = create_risk_gauge(
                    metric_name=event["metric"].replace("_", " ").title(),
                    current_value=event["current_value"],
                    limit_value=event["limit_value"],
                    utilization_pct=event["utilization_pct"],
                )
                gauges.append(dcc.Graph(figure=fig, config={"displayModeBar": False}))
            return gauges
    except Exception:
        pass
    return "한도 데이터 로딩 중..."


@app.callback(
    Output("risk-scenario-chart", "figure"),
    Input("interval-risk", "n_intervals"),
    prevent_initial_call=True,
)
def update_scenario_chart(_n: int):
    """시나리오 분석 차트 갱신."""
    import plotly.graph_objects as go

    try:
        resp = requests.get(f"{API_BASE}/risk/scenarios", timeout=10)
        if resp.ok:
            scenarios = resp.json()
            names = [s["scenario_name"] for s in scenarios.values()]
            pnls = [s["pnl"] for s in scenarios.values()]
            colors = ["#4caf50" if p >= 0 else "#e63946" for p in pnls]

            fig = go.Figure(
                go.Bar(
                    x=names,
                    y=pnls,
                    marker_color=colors,
                    text=[f"{p:,.0f}" for p in pnls],
                    textposition="outside",
                )
            )
            fig.add_hline(y=0, line_color="white", line_width=1)
            fig.update_layout(
                title="시나리오별 P&L",
                yaxis_title="P&L (원)",
                paper_bgcolor="#1a1a2e",
                plot_bgcolor="#1a1a2e",
                font_color="white",
                height=400,
                xaxis_tickangle=-30,
            )
            return fig
    except Exception:
        pass

    return go.Figure().update_layout(paper_bgcolor="#1a1a2e", font_color="white")
