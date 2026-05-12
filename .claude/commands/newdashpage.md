# newdashpage — 새 대시보드 페이지 생성

인자: `$ARGUMENTS`

인자 형식: `<page_id> "<Tab Label>"` (예: `pnl_tracker "P&L Tracker"`)
- `page_id`: 스네이크 케이스 파일명 (예: `pnl_tracker`)
- Tab Label (선택): 탭에 표시될 이름. 생략 시 page_id를 Title Case로 변환하여 사용.

인자가 비어 있으면 사용법을 안내하고 중단한다.

---

## 수행할 작업

다음 3가지 파일을 순서대로 수정/생성한다.

### 1. 페이지 파일 생성

경로: `src/hdesk/dashboard/pages/<page_id>.py`

아래 템플릿을 그대로 사용하되, 모든 `<PAGE_ID>`, `<PAGE_LABEL>` 플레이스홀더를 실제 값으로 치환한다.

```python
"""<PAGE_LABEL> 페이지"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html

API_BASE = "http://localhost:8000/api/v1"


def layout() -> dbc.Container:
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("<PAGE_LABEL>"),
                            dbc.CardBody(
                                html.Div(
                                    id="<PAGE_ID>-content",
                                    children=html.P("데이터를 불러오는 중...", className="text-muted"),
                                )
                            ),
                        ]
                    ),
                    width=12,
                ),
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("차트"),
                                dbc.CardBody(dcc.Graph(id="<PAGE_ID>-chart")),
                            ]
                        ),
                        width=8,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("요약"),
                                dbc.CardBody(html.Div(id="<PAGE_ID>-summary")),
                            ]
                        ),
                        width=4,
                    ),
                ],
                className="mb-3",
            ),
        ],
        fluid=True,
    )
```

### 2. layout.py 탭 등록

파일: `src/hdesk/dashboard/layout.py`

`dbc.Tabs` 블록의 마지막 `dbc.Tab(...)` 항목 뒤에 다음 줄을 추가한다.

```python
                    dbc.Tab(label="<TAB_LABEL>", tab_id="<PAGE_ID>"),
```

기존 탭 목록 예시 (참고용, 수정 금지):
```
dbc.Tab(label="Overview",       tab_id="overview"),
dbc.Tab(label="Greeks Monitor", tab_id="greeks"),
dbc.Tab(label="Vol Surface",    tab_id="vol-surface"),
dbc.Tab(label="Risk Report",    tab_id="risk"),
```

### 3. 탭 라우팅 콜백 등록

파일: `src/hdesk/dashboard/callbacks/greeks_cb.py`

`render_tab` 함수 상단의 import 문에 새 페이지 모듈을 추가한다.

```python
from hdesk.dashboard.pages import greeks_monitor, overview, <PAGE_ID>, risk_report, vol_surface
```

그리고 `render_tab` 함수의 `raise PreventUpdate` 직전에 다음 분기를 추가한다.

```python
    elif active_tab == "<PAGE_ID>":
        return <PAGE_ID>.layout()
```

---

## 완료 후 안내

작업이 끝나면 다음 내용을 사용자에게 알린다.

1. 생성/수정된 파일 목록 (경로 포함)
2. 새 탭 ID: `<PAGE_ID>`
3. 다음 단계 안내:
   - `src/hdesk/dashboard/callbacks/` 에 `<PAGE_ID>_cb.py` 콜백 파일을 추가하면 차트/요약 패널에 데이터를 연결할 수 있다.
   - 새 인터벌이 필요하면 `layout.py`의 `dcc.Interval` 섹션에 추가한다.
