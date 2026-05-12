"""Overview 페이지 - 포지션 현황 요약"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dash_table, html

API_BASE = "http://localhost:8000/api/v1"


def layout() -> dbc.Container:
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("포트폴리오 Greeks 요약"),
                                dbc.CardBody(html.Div(id="overview-portfolio-greeks")),
                            ]
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("리스크 한도"),
                                dbc.CardBody(html.Div(id="overview-limits")),
                            ]
                        ),
                        width=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("포지션 목록"),
                            dbc.CardBody(
                                dash_table.DataTable(
                                    id="overview-position-table",
                                    columns=[
                                        {"name": "ID", "id": "id"},
                                        {"name": "기초자산", "id": "underlying"},
                                        {"name": "구분", "id": "instrument_type"},
                                        {"name": "콜/풋", "id": "option_type"},
                                        {"name": "행사가", "id": "strike"},
                                        {"name": "만기", "id": "expiry"},
                                        {"name": "수량", "id": "quantity"},
                                        {"name": "평균가", "id": "avg_price"},
                                    ],
                                    style_table={"overflowX": "auto"},
                                    style_cell={
                                        "backgroundColor": "#2d2d2d",
                                        "color": "white",
                                        "textAlign": "right",
                                        "fontSize": "13px",
                                    },
                                    style_header={
                                        "backgroundColor": "#1a1a2e",
                                        "fontWeight": "bold",
                                    },
                                    page_size=20,
                                    sort_action="native",
                                    filter_action="native",
                                )
                            ),
                        ]
                    )
                )
            ),
        ],
        fluid=True,
    )
