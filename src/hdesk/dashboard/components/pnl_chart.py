"""P&L 차트 컴포넌트"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def create_pnl_chart(pnl_series: pd.Series, title: str = "누적 P&L") -> go.Figure:
    """누적 P&L 라인 차트.

    Args:
        pnl_series: 인덱스=날짜, 값=누적 P&L

    Returns:
        plotly Figure
    """
    cumulative = pnl_series.cumsum()
    color = "green" if cumulative.iloc[-1] >= 0 else "red"

    fig = go.Figure(
        go.Scatter(
            x=cumulative.index,
            y=cumulative.values,
            mode="lines",
            line=dict(color=color, width=2),
            fill="tozeroy",
            fillcolor=f"rgba({'0,128,0' if color == 'green' else '255,0,0'},0.1)",
            name="누적 P&L",
        )
    )
    fig.add_hline(y=0, line_color="white", line_dash="dash", line_width=1)
    fig.update_layout(
        title=title,
        xaxis_title="날짜",
        yaxis_title="P&L (원)",
        paper_bgcolor="#1a1a2e",
        plot_bgcolor="#1a1a2e",
        font_color="white",
        height=300,
    )
    return fig


def create_pnl_attribution_chart(attribution: dict) -> go.Figure:
    """P&L 어트리뷰션 바 차트."""
    labels = ["Delta", "Gamma", "Vega", "Theta", "Residual"]
    values = [
        attribution.get("delta_pnl", 0),
        attribution.get("gamma_pnl", 0),
        attribution.get("vega_pnl", 0),
        attribution.get("theta_pnl", 0),
        attribution.get("residual", 0),
    ]
    colors = ["#00b4d8" if v >= 0 else "#e63946" for v in values]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker_color=colors,
            text=[f"{v:,.0f}" for v in values],
            textposition="outside",
        )
    )
    fig.add_hline(y=0, line_color="white", line_width=1)
    fig.update_layout(
        title="P&L 어트리뷰션",
        yaxis_title="P&L (원)",
        paper_bgcolor="#1a1a2e",
        plot_bgcolor="#1a1a2e",
        font_color="white",
        height=300,
    )
    return fig
