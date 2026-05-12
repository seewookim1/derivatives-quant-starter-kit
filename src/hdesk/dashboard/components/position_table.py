"""포지션 테이블 컴포넌트"""

from __future__ import annotations

from dash import dash_table


POSITION_COLUMNS = [
    {"name": "ID", "id": "id", "type": "numeric"},
    {"name": "기초자산", "id": "underlying"},
    {"name": "구분", "id": "instrument_type"},
    {"name": "C/P", "id": "option_type"},
    {"name": "행사가", "id": "strike", "type": "numeric", "format": dash_table.FormatTemplate.money(0)},
    {"name": "만기", "id": "expiry"},
    {"name": "수량", "id": "quantity", "type": "numeric"},
    {"name": "평균가", "id": "avg_price", "type": "numeric"},
    {"name": "명목금액", "id": "notional", "type": "numeric", "format": dash_table.FormatTemplate.money(0)},
]

DARK_STYLE = {
    "style_table": {"overflowX": "auto"},
    "style_cell": {
        "backgroundColor": "#1e1e2f",
        "color": "white",
        "textAlign": "right",
        "fontSize": "13px",
        "padding": "6px 12px",
        "border": "1px solid #3d3d5c",
    },
    "style_header": {
        "backgroundColor": "#0d0d1a",
        "fontWeight": "bold",
        "color": "#00b4d8",
        "border": "1px solid #3d3d5c",
    },
    "style_data_conditional": [
        # 매수 포지션 (quantity > 0) → 녹색
        {
            "if": {"filter_query": "{quantity} > 0"},
            "color": "#4caf50",
        },
        # 매도 포지션 → 빨간색
        {
            "if": {"filter_query": "{quantity} < 0"},
            "color": "#e63946",
        },
    ],
}


def create_position_table(table_id: str = "position-table") -> dash_table.DataTable:
    return dash_table.DataTable(
        id=table_id,
        columns=POSITION_COLUMNS,
        page_size=25,
        sort_action="native",
        filter_action="native",
        export_format="xlsx",
        **DARK_STYLE,
    )
