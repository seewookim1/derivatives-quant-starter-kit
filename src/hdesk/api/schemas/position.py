"""포지션 Pydantic 스키마"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PositionCreate(BaseModel):
    underlying: str = Field(..., examples=["KOSPI200"])
    instrument_type: str = Field(..., examples=["OPTION"])
    option_type: Optional[str] = Field(default=None, examples=["C"])
    strike: Optional[float] = Field(default=None, examples=[350.0])
    expiry: Optional[date] = Field(default=None, examples=["2025-06-12"])
    quantity: int = Field(..., examples=[10])
    multiplier: int = Field(default=250_000)
    avg_price: float = Field(..., examples=[5.50])


class PositionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    underlying: str
    instrument_type: str
    option_type: Optional[str]
    strike: Optional[float]
    expiry: Optional[date]
    quantity: int
    multiplier: int
    avg_price: float
    is_active: bool
    created_at: datetime
    notional: float


class TradeCreate(BaseModel):
    position_id: int
    quantity: int
    price: float
    side: str = Field(..., examples=["BUY"])
    commission: float = Field(default=0.0)
