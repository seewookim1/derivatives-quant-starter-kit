"""Greeks 실시간 모니터링 페이지"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html


def layout() -> dbc.Container:
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("표시할 Greek:"),
                            dcc.Dropdown(
                                id="greeks-metric-selector",
                                options=[
                                    {"label": "Delta", "value": "delta"},
                                    {"label": "Gamma", "value": "gamma"},
                                    {"label": "Vega", "value": "vega"},
                                    {"label": "Theta", "value": "theta"},
                                ],
                                value="delta",
                                clearable=False,
                                style={"backgroundColor": "#2d2d2d", "color": "#fff"},
                            ),
                        ],
                        width=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("기초자산:"),
                            dcc.Dropdown(
                                id="greeks-underlying-selector",
                                options=[
                                    {"label": "KOSPI200", "value": "KOSPI200"},
                                    {"label": "삼성전자", "value": "005930 KS"},
                                ],
                                value="KOSPI200",
                                clearable=False,
                                style={"backgroundColor": "#2d2d2d"},
                            ),
                        ],
                        width=3,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Greeks 히트맵 (Strike x Expiry)"),
                                dbc.CardBody(dcc.Graph(id="greeks-heatmap")),
                            ]
                        ),
                        width=8,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("포트폴리오 Greeks"),
                                dbc.CardBody(html.Div(id="greeks-portfolio-summary")),
                            ]
                        ),
                        width=4,
                    ),
                ]
            ),
        ],
        fluid=True,
    )
