"""시장 데이터 및 Greeks 스냅샷 ORM 모델 (TimescaleDB 하이퍼테이블)

TimescaleDB 하이퍼테이블은 init.sql에서 직접 DDL로 생성.
여기서는 SQLAlchemy 매핑만 정의하여 쿼리에 사용.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from hdesk.data.database import Base


class MarketData(Base):
    """틱 데이터 (TimescaleDB 하이퍼테이블 - init.sql에서 생성)."""

    __tablename__ = "market_data"

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(30), primary_key=True)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bid: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ask: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volume: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)


class GreeksSnapshot(Base):
    """Greeks 시계열 스냅샷 (TimescaleDB 하이퍼테이블)."""

    __tablename__ = "greeks_snapshots"

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    position_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    delta: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gamma: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    vega: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    theta: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rho: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    option_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    implied_vol: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
