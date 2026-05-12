"""포지션 라우터"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from hdesk.api.deps import get_db
from hdesk.api.schemas.position import PositionCreate, PositionResponse
from hdesk.data.models.position import Position
from hdesk.data.repositories.position_repo import PositionRepository

router = APIRouter(prefix="/positions", tags=["positions"])


@router.get("", response_model=list[PositionResponse])
async def list_positions(db: AsyncSession = Depends(get_db)) -> list[PositionResponse]:
    repo = PositionRepository(db)
    positions = await repo.get_all_active()
    return [PositionResponse.model_validate(p) for p in positions]


@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(
    position_id: int,
    db: AsyncSession = Depends(get_db),
) -> PositionResponse:
    repo = PositionRepository(db)
    position = await repo.get_by_id(position_id)
    if not position:
        raise HTTPException(status_code=404, detail="포지션을 찾을 수 없습니다")
    return PositionResponse.model_validate(position)


@router.post("", response_model=PositionResponse, status_code=201)
async def create_position(
    data: PositionCreate,
    db: AsyncSession = Depends(get_db),
) -> PositionResponse:
    repo = PositionRepository(db)
    position = Position(**data.model_dump())
    created = await repo.create(position)
    return PositionResponse.model_validate(created)


@router.delete("/{position_id}", status_code=204)
async def deactivate_position(
    position_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    repo = PositionRepository(db)
    position = await repo.get_by_id(position_id)
    if not position:
        raise HTTPException(status_code=404, detail="포지션을 찾을 수 없습니다")
    await repo.deactivate(position_id)
