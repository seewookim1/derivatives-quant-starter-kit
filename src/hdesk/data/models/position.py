"""포지션 및 거래 ORM 모델"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hdesk.data.database import Base


class Position(Base):
    """현재 보유 포지션."""

    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    underlying: Mapped[str] = mapped_column(String(30))        # 예: "005930 KS", "KOSPI200"
    instrument_type: Mapped[str] = mapped_column(String(10))   # "OPTION" or "FUTURE"
    option_type: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)  # "C" or "P"
    strike: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    expiry: Mapped[Optional[date]] = mapped_column(nullable=True)
    quantity: Mapped[int] = mapped_column(Integer)             # 양수=매수, 음수=매도
    multiplier: Mapped[int] = mapped_column(Integer, default=250_000)  # KOSPI200 기본값
    avg_price: Mapped[float] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(default=True)

    trades: Mapped[list["Trade"]] = relationship("Trade", back_populates="position")

    @property
    def notional(self) -> float:
        """명목 금액."""
        return abs(self.quantity) * self.avg_price * self.multiplier

    @property
    def is_long(self) -> bool:
        return self.quantity > 0


class Trade(Base):
    """개별 거래 기록 (불변 원장)."""

    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    position_id: Mapped[int] = mapped_column(Integer, ForeignKey("positions.id"))
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    side: Mapped[str] = mapped_column(String(4))  # "BUY" or "SELL"
    commission: Mapped[float] = mapped_column(Float, default=0.0)

    position: Mapped["Position"] = relationship("Position", back_populates="trades")
