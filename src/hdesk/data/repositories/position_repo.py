"""포지션 레포지토리 - CRUD"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from hdesk.data.models.position import Position, Trade


class PositionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all_active(self) -> list[Position]:
        result = await self._session.execute(
            select(Position).where(Position.is_active == True)  # noqa: E712
        )
        return list(result.scalars().all())

    async def get_by_id(self, position_id: int) -> Optional[Position]:
        return await self._session.get(Position, position_id)

    async def get_by_underlying(self, underlying: str) -> list[Position]:
        result = await self._session.execute(
            select(Position).where(
                Position.underlying == underlying,
                Position.is_active == True,  # noqa: E712
            )
        )
        return list(result.scalars().all())

    async def create(self, position: Position) -> Position:
        self._session.add(position)
        await self._session.flush()
        return position

    async def create_trade(self, trade: Trade) -> Trade:
        self._session.add(trade)
        await self._session.flush()
        return trade

    async def deactivate(self, position_id: int) -> None:
        await self._session.execute(
            update(Position)
            .where(Position.id == position_id)
            .values(is_active=False)
        )
