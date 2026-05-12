"""Bloomberg BLP API 피드 연동"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from hdesk.workers.feeds.base_feed import BaseFeed, Tick

logger = logging.getLogger(__name__)


class BloombergFeed(BaseFeed):
    """Bloomberg API (blp) 기반 실시간 시장 데이터 피드.

    blp 0.0.3: https://pypi.org/project/blp/
    Bloomberg Terminal에 연결된 환경에서만 동작.
    """

    def __init__(self, redis_client, db_session_factory) -> None:
        self._redis = redis_client
        self._db_session_factory = db_session_factory
        self._session = None

    async def connect(self) -> None:
        try:
            import blp

            loop = asyncio.get_event_loop()
            self._session = await loop.run_in_executor(None, blp.BLPInterface)
            logger.info("Bloomberg 연결 성공")
        except ImportError:
            logger.warning("blp 패키지 미설치 - Bloomberg 연동 비활성화")
        except Exception as e:
            logger.error("Bloomberg 연결 실패: %s", e)

    async def disconnect(self) -> None:
        if self._session:
            self._session = None
            logger.info("Bloomberg 연결 종료")

    async def subscribe(self, symbols: list[str]) -> None:
        if self._session is None:
            logger.warning("Bloomberg 미연결 - 구독 스킵")
            return
        # 실제 구현: blp.subscribe() 콜백 등록
        logger.info("Bloomberg 구독: %s", symbols)

    async def on_tick(self, tick: Tick) -> None:
        """틱 수신 시 DB 저장 + Redis 발행."""
        import json

        from hdesk.data.models.market_data import MarketData

        # Redis 발행
        await self._redis.publish(
            "feed:ticks",
            json.dumps({
                "symbol": tick.symbol,
                "price": tick.price,
                "bid": tick.bid,
                "ask": tick.ask,
                "timestamp": tick.timestamp.isoformat(),
            }),
        )

        # DB 저장
        async with self._db_session_factory() as session:
            md = MarketData(
                timestamp=tick.timestamp,
                symbol=tick.symbol,
                price=tick.price,
                bid=tick.bid,
                ask=tick.ask,
                volume=tick.volume,
            )
            session.add(md)


class SimulatedFeed(BaseFeed):
    """테스트/개발용 시뮬레이션 피드."""

    def __init__(self, redis_client, interval_seconds: float = 1.0) -> None:
        self._redis = redis_client
        self._interval = interval_seconds
        self._running = False
        self._symbols: list[str] = []

    async def connect(self) -> None:
        self._running = True
        logger.info("SimulatedFeed 시작")

    async def disconnect(self) -> None:
        self._running = False

    async def subscribe(self, symbols: list[str]) -> None:
        self._symbols = symbols
        asyncio.create_task(self._tick_loop())

    async def _tick_loop(self) -> None:
        import random
        import json

        prices = {s: 350.0 for s in self._symbols}
        while self._running:
            for symbol in self._symbols:
                # 랜덤 워크
                prices[symbol] *= 1 + random.gauss(0, 0.001)
                tick = Tick(
                    symbol=symbol,
                    timestamp=datetime.utcnow(),
                    price=prices[symbol],
                    bid=prices[symbol] - 0.05,
                    ask=prices[symbol] + 0.05,
                    volume=random.randint(100, 10000),
                )
                await self.on_tick(tick)
            await asyncio.sleep(self._interval)

    async def on_tick(self, tick: Tick) -> None:
        import json

        await self._redis.publish(
            "feed:ticks",
            json.dumps({
                "symbol": tick.symbol,
                "price": tick.price,
                "timestamp": tick.timestamp.isoformat(),
            }),
        )
