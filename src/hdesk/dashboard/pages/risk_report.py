"""리스크 보고서 페이지 - VaR / 시나리오 분석"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html


def layout() -> dbc.Container:
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("VaR 결과"),
                                dbc.CardBody(html.Div(id="risk-var-result")),
                            ]
                        ),
                        width=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("P&L 분포"),
                                dbc.CardBody(dcc.Graph(id="risk-pnl-histogram")),
                            ]
                        ),
                        width=8,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("시나리오 분석"),
                            dbc.CardBody(dcc.Graph(id="risk-scenario-chart")),
                        ]
                    )
                )
            ),
        ],
        fluid=True,
    )
