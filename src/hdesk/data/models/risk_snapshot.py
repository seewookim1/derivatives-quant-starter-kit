"""리스크 계산 결과 ORM 모델"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from hdesk.data.database import Base


class VaRResult(Base):
    """VaR 계산 결과 저장."""

    __tablename__ = "var_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    calc_date: Mapped[date] = mapped_column(Date)
    method: Mapped[str] = mapped_column(String(20))         # "historical" or "parametric"
    confidence: Mapped[float] = mapped_column(Float)        # 0.99
    horizon_days: Mapped[int] = mapped_column(Integer)      # 1
    var_amount: Mapped[float] = mapped_column(Float)        # 손실액 (원화)
    cvar_amount: Mapped[float] = mapped_column(Float)       # Expected Shortfall
    lookback_days: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
