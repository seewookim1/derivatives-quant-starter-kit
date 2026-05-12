"""변동성 서피스 3D 시각화 페이지"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html


def layout() -> dbc.Container:
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.Label("기초자산:"),
                        dcc.Dropdown(
                            id="vol-underlying-selector",
                            options=[
                                {"label": "KOSPI200", "value": "KOSPI200"},
                                {"label": "삼성전자", "value": "005930 KS"},
                            ],
                            value="KOSPI200",
                            clearable=False,
                            style={"width": "300px"},
                        ),
                    ]
                ),
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("변동성 서피스 (3D)"),
                                dbc.CardBody(dcc.Graph(id="vol-surface-3d", style={"height": "500px"})),
                            ]
                        ),
                        width=7,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("스마일 곡선 (만기별)"),
                                dbc.CardBody(dcc.Graph(id="vol-smile-chart")),
                            ]
                        ),
                        width=5,
                    ),
                ]
            ),
        ],
        fluid=True,
    )
