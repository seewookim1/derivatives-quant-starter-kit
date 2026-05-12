"""Greeks 라우터"""

from __future__ import annotations

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from hdesk.api.deps import get_db
from hdesk.api.schemas.greeks import GreeksResponse, PortfolioGreeksResponse
from hdesk.data.repositories.market_data_repo import MarketDataRepository
from hdesk.data.repositories.position_repo import PositionRepository
from hdesk.pricing.greeks import compute_all_greeks
from hdesk.pricing.vol_surface import VolSurface
from hdesk.risk.greeks_agg import aggregate_portfolio_greeks
from hdesk.utils.config import get_settings
from hdesk.utils.date_utils import years_to_expiry

router = APIRouter(prefix="/greeks", tags=["greeks"])
settings = get_settings()


@router.get("/positions/{position_id}", response_model=GreeksResponse)
async def get_position_greeks(
    position_id: int,
    spot_override: float | None = Query(default=None, description="기초자산 가격 오버라이드"),
    vol_override: float | None = Query(default=None, description="변동성 오버라이드"),
    db: AsyncSession = Depends(get_db),
) -> GreeksResponse:
    repo = PositionRepository(db)
    md_repo = MarketDataRepository(db)

    position = await repo.get_by_id(position_id)
    if not position or position.instrument_type != "OPTION":
        raise HTTPException(status_code=404, detail="옵션 포지션을 찾을 수 없습니다")

    if position.expiry is None or position.strike is None:
        raise HTTPException(status_code=400, detail="포지션에 만기/행사가 정보가 없습니다")

    # 시장 데이터 조회
    S = spot_override or await md_repo.get_latest_price(position.underlying) or 0.0
    if S == 0:
        raise HTTPException(status_code=422, detail=f"시장 데이터 없음: {position.underlying}")

    T = years_to_expiry(position.expiry)
    K = position.strike
    r = settings.default_risk_free_rate
    sigma = vol_override or 0.20  # 실제는 VolSurface에서 조회

    from hdesk.pricing.black_scholes import bs_price
    option_price = float(bs_price(S, K, T, r, sigma, position.option_type or "C"))

    g = compute_all_greeks(
        S=np.array([S]),
        K=np.array([K]),
        T=np.array([T]),
        r=np.array([r]),
        sigma=np.array([sigma]),
        option_type=np.array([position.option_type or "C"]),
    )

    return GreeksResponse(
        position_id=position_id,
        delta=float(g.delta[0]),
        gamma=float(g.gamma[0]),
        vega=float(g.vega[0]),
        theta=float(g.theta[0]),
        rho=float(g.rho[0]),
        vanna=float(g.vanna[0]),
        volga=float(g.volga[0]),
        implied_vol=sigma,
        option_price=option_price,
        underlying_price=S,
    )


@router.get("/portfolio", response_model=PortfolioGreeksResponse)
async def get_portfolio_greeks(db: AsyncSession = Depends(get_db)) -> PortfolioGreeksResponse:
    repo = PositionRepository(db)
    md_repo = MarketDataRepository(db)
    positions = await repo.get_all_active()

    greeks_map = {}
    for pos in positions:
        if pos.instrument_type != "OPTION" or pos.expiry is None or pos.strike is None:
            continue
        S = await md_repo.get_latest_price(pos.underlying) or 350.0
        T = years_to_expiry(pos.expiry)
        g = compute_all_greeks(
            S=np.array([S]),
            K=np.array([pos.strike]),
            T=np.array([T]),
            r=np.array([settings.default_risk_free_rate]),
            sigma=np.array([0.20]),
            option_type=np.array([pos.option_type or "C"]),
        )
        greeks_map[pos.id] = g

    portfolio = aggregate_portfolio_greeks(positions, greeks_map)
    return PortfolioGreeksResponse(**portfolio.to_dict())
