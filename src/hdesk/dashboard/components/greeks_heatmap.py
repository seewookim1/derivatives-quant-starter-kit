"""Greeks 히트맵 컴포넌트 - Strike x Expiry"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go


def create_greeks_heatmap(
    greeks_df: pd.DataFrame,
    metric: str = "delta",
    title: str | None = None,
) -> go.Figure:
    """Greeks 히트맵 생성.

    Args:
        greeks_df: 컬럼 = [strike, expiry, delta, gamma, vega, theta]
        metric: 표시할 Greek
        title: 차트 제목

    Returns:
        plotly Figure
    """
    if greeks_df.empty:
        return go.Figure().update_layout(
            title="데이터 없음",
            paper_bgcolor="#1a1a2e",
            plot_bgcolor="#1a1a2e",
            font_color="white",
        )

    pivot = greeks_df.pivot(index="expiry", columns="strike", values=metric)

    # 색상 스케일: delta는 RdBu, gamma/vega는 Viridis
    colorscale = "RdBu" if metric == "delta" else "Viridis"
    zmid = 0 if metric == "delta" else None

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=[f"{k:,.0f}" for k in pivot.columns],
            y=[str(e) for e in pivot.index],
            colorscale=colorscale,
            zmid=zmid,
            colorbar=dict(title=metric.capitalize(), tickfont=dict(color="white")),
            hovertemplate=f"Strike: %{{x}}<br>Expiry: %{{y}}<br>{metric}: %{{z:.4f}}<extra></extra>",
        )
    )

    fig.update_layout(
        title=title or f"{metric.capitalize()} Heatmap",
        xaxis_title="Strike",
        yaxis_title="Expiry",
        paper_bgcolor="#1a1a2e",
        plot_bgcolor="#1a1a2e",
        font_color="white",
        height=400,
    )

    return fig
