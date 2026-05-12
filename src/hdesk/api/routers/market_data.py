"""시장 데이터 라우터"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from hdesk.api.deps import get_db
from hdesk.data.repositories.market_data_repo import MarketDataRepository
from hdesk.pricing.vol_surface import VolSurface

router = APIRouter(prefix="/market-data", tags=["market-data"])


class VolSurfaceResponse(BaseModel):
    underlying: str
    strikes: list[float]
    expiries: list[float]
    vols: list[list[float]]


@router.get("/vol-surface/{underlying}", response_model=VolSurfaceResponse)
async def get_vol_surface(
    underlying: str,
    db: AsyncSession = Depends(get_db),
) -> VolSurfaceResponse:
    # 실제 구현에서는 Redis 캐시 → DB 순으로 조회
    # 여기서는 데모용 플랫 서피스 반환
    surface = VolSurface.flat(0.20, underlying)
    return VolSurfaceResponse(
        underlying=underlying,
        strikes=surface.strikes.tolist(),
        expiries=surface.expiries.tolist(),
        vols=surface.vols.tolist(),
    )


class PriceResponse(BaseModel):
    symbol: str
    price: float | None


@router.get("/price/{symbol}", response_model=PriceResponse)
async def get_latest_price(
    symbol: str,
    db: AsyncSession = Depends(get_db),
) -> PriceResponse:
    repo = MarketDataRepository(db)
    price = await repo.get_latest_price(symbol)
    return PriceResponse(symbol=symbol, price=price)
