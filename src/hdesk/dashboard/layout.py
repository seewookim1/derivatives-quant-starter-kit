"""대시보드 전체 레이아웃"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_layout() -> dbc.Container:
    return dbc.Container(
        [
            # 헤더
            dbc.NavbarSimple(
                brand="HDesk Risk Monitor",
                brand_href="#",
                color="dark",
                dark=True,
                className="mb-3",
                children=[
                    dbc.NavItem(dbc.NavLink("API Docs", href="http://localhost:8000/docs", target="_blank")),
                ],
            ),
            # 탭 네비게이션
            dbc.Tabs(
                [
                    dbc.Tab(label="Overview", tab_id="overview"),
                    dbc.Tab(label="Greeks Monitor", tab_id="greeks"),
                    dbc.Tab(label="Vol Surface", tab_id="vol-surface"),
                    dbc.Tab(label="Risk Report", tab_id="risk"),
                ],
                id="tabs",
                active_tab="overview",
                className="mb-3",
            ),
            # 탭 콘텐츠
            html.Div(id="tab-content"),
            # 자동 갱신 인터벌
            dcc.Interval(id="interval-greeks", interval=5_000, n_intervals=0),    # 5초
            dcc.Interval(id="interval-positions", interval=10_000, n_intervals=0), # 10초
            dcc.Interval(id="interval-risk", interval=60_000, n_intervals=0),      # 1분
            # 클라이언트 사이드 캐시
            dcc.Store(id="store-positions"),
            dcc.Store(id="store-portfolio-greeks"),
        ],
        fluid=True,
        className="px-4",
    )
