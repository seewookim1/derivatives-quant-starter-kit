# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

HDesk — 파생상품 헤지 데스크 리스크 관리 시스템. Python 3.9 전용.  
4개의 독립 프로세스로 구성: API 서버, Dash 대시보드, APScheduler 워커, DB 초기화.

## 개발 환경 설정

```bash
pip install -e ".[dev]"
# Bloomberg 피드 포함 시
pip install -e ".[dev,bloomberg]"
```

`.env` 파일로 설정 주입 (`src/hdesk/utils/config.py` 참고). 미설정 시 기본값(localhost PostgreSQL/Redis)으로 동작.

## 주요 실행 명령어

```bash
hdesk-api        # FastAPI 서버 (기본 :8000)
hdesk-dash       # Dash 대시보드 (기본 :8050)
hdesk-worker     # APScheduler 배치 워커
hdesk-initdb     # DB 테이블 생성 + 시드 데이터
```

개발 중 API 자동 재로딩:
```bash
uvicorn hdesk.api.main:app --reload --port 8000
```

## 테스트

```bash
# 유닛 테스트만 (DB/Redis 불필요)
pytest tests/unit/ -v --tb=short

# 단일 테스트 파일
pytest tests/unit/test_black_scholes.py -v

# 단일 테스트 케이스
pytest tests/unit/test_greeks.py::test_delta_call -v

# 통합 테스트 (PostgreSQL + Redis 실행 필요)
pytest tests/integration/
```

`conftest.py`의 공용 픽스처: `sample_option_params`(KOSPI200 ATM 콜 파라미터), `vol_surface_data`(스큐 포함 5×7 격자).

## 린트 / 타입 체크

```bash
ruff check src/
ruff format src/
black src/          # 포매터 (line-length=100)
mypy src/           # strict=false
```

## 아키텍처

### 레이어 구조와 의존 방향

```
pricing/ (순수 수학)
    ↓
risk/   (포지션 집계, VaR, 시나리오)
    ↓
data/   (ORM 모델, 비동기 리포지토리)
    ↓
api/    (FastAPI 라우터, WebSocket)
    ↑
dashboard/ (Dash — REST 폴링)
workers/   (APScheduler 배치)
```

### `src/hdesk/pricing/`

I/O가 전혀 없는 순수 수학 계층. 모든 함수가 numpy 벡터화 설계(`np.ndarray | float` 시그니처).  
- `black_scholes.py` — `bs_price`, `bs_d1_d2` (Greeks 계산의 공통 기반)
- `greeks.py` — `GreeksResult` 데이터클래스, 포지션별 Greeks 계산
- `implied_vol.py` — Newton-Raphson + py_lets_be_rational 기반 내재변동성
- `vol_surface.py` — 파라메트릭 변동성 서피스 보간
- `american.py` — QuantLib 기반 미국식 옵션 프라이싱

### `src/hdesk/risk/`

포지션 목록 + Greeks를 입력받아 포트폴리오 단위 집계.  
- `greeks_agg.py` — `PortfolioGreeks` (기초자산별/만기별 버킷 포함), `aggregate_portfolio_greeks()`
- `var.py` — 역사적 VaR (252영업일 기본)
- `limits.py` — `net_delta ≤ 1000`, `net_vega ≤ 500,000` 한도 검사

### `src/hdesk/data/`

SQLAlchemy 2.0 비동기 엔진(`asyncpg`) + 동기 엔진(`psycopg2`, Alembic 전용).  
**TimescaleDB 하이퍼테이블은 Alembic이 아닌 `init.sql`에서 직접 생성** — `alembic revision`으로 건드리지 않는다.  
리포지토리 패턴: 라우터 → `api/deps.py`의 `get_db` 의존성 → `AsyncSession` → 리포지토리.

### `src/hdesk/api/`

FastAPI 비동기 라우터. `lifespan` 컨텍스트에서 DB 초기화, Redis 연결, WebSocket 리스너 시작.  
- WebSocket(`/ws/greeks`, `/ws/pnl`)은 Redis Pub/Sub 채널(`greeks:updates`, `risk:portfolio`)을 구독해 브라우저로 브로드캐스트
- 모든 설정은 `get_settings()` (`@lru_cache(maxsize=1)`)로 접근

### `src/hdesk/dashboard/`

Dash 앱의 데이터는 **REST API 폴링** 방식(`requests` 동기 호출, `API_BASE = "http://localhost:8000/api/v1"`).  
콜백 등록 순서가 중요: `app.py`에서 layout 설정 후 callbacks 임포트 (`suppress_callback_exceptions=True`).

**새 탭 페이지 추가 시 3곳을 수정해야 한다:**
1. `pages/<page_id>.py` — `layout() -> dbc.Container` 구현
2. `layout.py` — `dbc.Tabs`에 `dbc.Tab(label=..., tab_id=...)` 추가
3. `callbacks/greeks_cb.py` — `render_tab()` 분기 및 import 추가

> `/newdashpage` 커스텀 커맨드가 이 3단계를 자동으로 수행한다.

**갱신 인터벌**: Greeks 5초, 포지션 10초, 리스크 1분.

### `src/hdesk/workers/`

`BlockingScheduler` (timezone=`Asia/Seoul`):
- EOD VaR: 평 16:30 KST
- Vol Surface 재보정: 장중 5분마다
- EOD P&L 보고서: 평 17:00 KST

시장 데이터 피드는 `BaseFeed` ABC 구현. Bloomberg 피드는 선택 의존성(`bloomberg` extra).
