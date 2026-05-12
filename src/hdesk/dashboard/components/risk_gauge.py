"""리스크 한도 게이지 컴포넌트"""

from __future__ import annotations

import plotly.graph_objects as go


def create_risk_gauge(
    metric_name: str,
    current_value: float,
    limit_value: float,
    utilization_pct: float,
) -> go.Figure:
    """리스크 한도 게이지 차트.

    Args:
        metric_name: 메트릭 이름 (예: 'Net Delta')
        current_value: 현재 값
        limit_value: 한도 값
        utilization_pct: 한도 대비 사용률 (%)
    """
    # 80% 이상 경고, 100% 초과 위반
    if utilization_pct >= 100:
        bar_color = "#e63946"
    elif utilization_pct >= 80:
        bar_color = "#ff9800"
    else:
        bar_color = "#4caf50"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=utilization_pct,
            delta={"reference": 80, "suffix": "%"},
            title={"text": metric_name, "font": {"color": "white"}},
            number={"suffix": "%", "font": {"color": "white"}},
            gauge={
                "axis": {"range": [0, 120], "tickcolor": "white"},
                "bar": {"color": bar_color},
                "steps": [
                    {"range": [0, 80], "color": "#1e1e2f"},
                    {"range": [80, 100], "color": "#3d2a00"},
                    {"range": [100, 120], "color": "#3d0000"},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 2},
                    "thickness": 0.75,
                    "value": 100,
                },
            },
        )
    )

    fig.add_annotation(
        text=f"현재: {current_value:,.0f} / 한도: {limit_value:,.0f}",
        x=0.5, y=0.15,
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(color="white", size=11),
    )

    fig.update_layout(
        paper_bgcolor="#1a1a2e",
        font_color="white",
        height=250,
        margin=dict(t=60, b=20, l=20, r=20),
    )
    return fig
