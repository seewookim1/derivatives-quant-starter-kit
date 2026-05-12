"""리스크 라우터"""

from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from hdesk.api.deps import get_db
from hdesk.api.schemas.risk import LimitCheckResponse, ScenarioResponse, VaRResponse
from hdesk.data.repositories.market_data_repo import MarketDataRepository
from hdesk.data.repositories.position_repo import PositionRepository
from hdesk.pricing.vol_surface import VolSurface
from hdesk.risk.limits import check_limits
from hdesk.risk.scenario import SCENARIOS, run_all_scenarios, run_scenario
from hdesk.risk.var import VaRResult, historical_var
from hdesk.utils.config import get_settings

router = APIRouter(prefix="/risk", tags=["risk"])
settings = get_settings()


@router.get("/var", response_model=VaRResponse)
async def get_var(
    method: str = Query(default="historical", description="historical | parametric"),
    confidence: float = Query(default=0.99),
    horizon_days: int = Query(default=1),
    db: AsyncSession = Depends(get_db),
) -> VaRResponse:
    md_repo = MarketDataRepository(db)

    if method == "historical":
        # KOSPI200 일별 수익률 조회
        price_df = await md_repo.get_price_history("KOSPI200", days=settings.default_var_lookback_days)
        if len(price_df) < 10:
            raise HTTPException(status_code=422, detail="히스토리 데이터 부족")

        returns = price_df["close"].pct_change().dropna()
        result = historical_var(
            returns=pd.Series(returns.values),
            confidence=confidence,
            horizon_days=horizon_days,
            lookback_days=settings.default_var_lookback_days,
        )
    else:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 방법: {method}")

    return VaRResponse(
        var_amount=result.var_amount,
        cvar_amount=result.cvar_amount,
        confidence=result.confidence,
        horizon_days=result.horizon_days,
        method=result.method,
        lookback_days=result.lookback_days,
    )


@router.get("/scenarios", response_model=dict[str, ScenarioResponse])
async def get_all_scenarios(db: AsyncSession = Depends(get_db)) -> dict[str, ScenarioResponse]:
    pos_repo = PositionRepository(db)
    md_repo = MarketDataRepository(db)

    positions = await pos_repo.get_all_active()
    spot_prices = {}
    for pos in positions:
        if pos.underlying not in spot_prices:
            price = await md_repo.get_latest_price(pos.underlying)
            spot_prices[pos.underlying] = price or 350.0

    vol_surface = VolSurface.flat(0.20, "KOSPI200")
    results = run_all_scenarios(positions, spot_prices, vol_surface)

    return {
        key: ScenarioResponse(
            scenario_name=r.scenario_name,
            spot_shock=r.spot_shock,
            vol_shock=r.vol_shock,
            pnl=r.pnl,
            new_delta=r.new_delta,
            new_vega=r.new_vega,
        )
        for key, r in results.items()
    }


@router.get("/scenarios/{scenario_key}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_key: str,
    db: AsyncSession = Depends(get_db),
) -> ScenarioResponse:
    if scenario_key not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"시나리오 없음: {scenario_key}")

    pos_repo = PositionRepository(db)
    md_repo = MarketDataRepository(db)

    positions = await pos_repo.get_all_active()
    spot_prices = {}
    for pos in positions:
        if pos.underlying not in spot_prices:
            price = await md_repo.get_latest_price(pos.underlying)
            spot_prices[pos.underlying] = price or 350.0

    vol_surface = VolSurface.flat(0.20, "KOSPI200")
    result = run_scenario(positions, spot_prices, vol_surface, scenario_key)

    return ScenarioResponse(
        scenario_name=result.scenario_name,
        spot_shock=result.spot_shock,
        vol_shock=result.vol_shock,
        pnl=result.pnl,
        new_delta=result.new_delta,
        new_vega=result.new_vega,
    )


@router.get("/limits", response_model=list[LimitCheckResponse])
async def get_limit_check(db: AsyncSession = Depends(get_db)) -> list[LimitCheckResponse]:
    import numpy as np

    from hdesk.data.repositories.market_data_repo import MarketDataRepository
    from hdesk.pricing.greeks import compute_all_greeks
    from hdesk.risk.greeks_agg import aggregate_portfolio_greeks
    from hdesk.utils.date_utils import years_to_expiry

    pos_repo = PositionRepository(db)
    md_repo = MarketDataRepository(db)

    positions = await pos_repo.get_all_active()
    greeks_map = {}
    for pos in positions:
        if pos.instrument_type != "OPTION" or pos.expiry is None or pos.strike is None:
            continue
        S = await md_repo.get_latest_price(pos.underlying) or 350.0
        T = years_to_expiry(pos.expiry)
        g = compute_all_greeks(
            S=np.array([S]), K=np.array([pos.strike]), T=np.array([T]),
            r=np.array([settings.default_risk_free_rate]),
            sigma=np.array([0.20]),
            option_type=np.array([pos.option_type or "C"]),
        )
        greeks_map[pos.id] = g

    portfolio = aggregate_portfolio_greeks(positions, greeks_map)
    events = check_limits(portfolio)

    return [LimitCheckResponse(**e.to_dict()) for e in events]
