"""Dash 애플리케이션 진입점"""

from __future__ import annotations

import dash
import dash_bootstrap_components as dbc

from hdesk.dashboard.layout import create_layout
from hdesk.utils.config import get_settings

settings = get_settings()

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],  # 트레이딩 데스크 다크 테마
    suppress_callback_exceptions=True,
    title="HDesk Risk Monitor",
)

app.layout = create_layout()

# 콜백 등록 (임포트 순서 중요)
from hdesk.dashboard.callbacks import greeks_cb, position_cb, risk_cb  # noqa: E402, F401


def run() -> None:
    app.run(
        host=settings.dash_host,
        port=settings.dash_port,
        debug=settings.api_debug,
    )


if __name__ == "__main__":
    run()
