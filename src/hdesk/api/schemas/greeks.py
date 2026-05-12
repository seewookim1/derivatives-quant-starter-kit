"""Greeks Pydantic 스키마"""

from __future__ import annotations

from pydantic import BaseModel


class GreeksResponse(BaseModel):
    position_id: int
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
    vanna: float
    volga: float
    implied_vol: float
    option_price: float
    underlying_price: float


class PortfolioGreeksResponse(BaseModel):
    net_delta: float
    net_gamma: float
    net_vega: float
    net_theta: float
    net_rho: float
    delta_by_underlying: dict[str, float]
    vega_by_expiry: dict[str, float]
    gamma_by_underlying: dict[str, float]
    position_count: int
