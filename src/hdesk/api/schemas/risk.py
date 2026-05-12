"""리스크 Pydantic 스키마"""

from __future__ import annotations

from pydantic import BaseModel


class VaRResponse(BaseModel):
    var_amount: float
    cvar_amount: float
    confidence: float
    horizon_days: int
    method: str
    lookback_days: int


class ScenarioResponse(BaseModel):
    scenario_name: str
    spot_shock: float
    vol_shock: float
    pnl: float
    new_delta: float
    new_vega: float


class LimitCheckResponse(BaseModel):
    metric: str
    current_value: float
    limit_value: float
    utilization_pct: float
    is_breach: bool
