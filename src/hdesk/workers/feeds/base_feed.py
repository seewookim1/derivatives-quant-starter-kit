"""시장 데이터 피드 추상 기반 클래스"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Tick:
    symbol: str
    timestamp: datetime
    price: float
    bid: float
    ask: float
    volume: int


class BaseFeed(ABC):
    """시장 데이터 피드 인터페이스."""

    @abstractmethod
    async def connect(self) -> None:
        """피드 서버 연결."""

    @abstractmethod
    async def disconnect(self) -> None:
        """연결 종료."""

    @abstractmethod
    async def subscribe(self, symbols: list[str]) -> None:
        """심볼 구독."""

    @abstractmethod
    async def on_tick(self, tick: Tick) -> None:
        """틱 수신 핸들러 - 하위 클래스에서 구현."""

    async def start(self, symbols: list[str]) -> None:
        """피드 시작 진입점."""
        await self.connect()
        await self.subscribe(symbols)
