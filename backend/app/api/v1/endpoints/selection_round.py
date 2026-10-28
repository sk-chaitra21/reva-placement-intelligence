from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_reviewer
from app.db.session import get_db
from app.models.placement_drive import PlacementDrive
from app.models.selection_round import SelectionRound
from app.models.user import User
from app.schemas.selection_round import SelectionRoundCreate, SelectionRoundResponse

router = APIRouter(
    prefix="/selection-rounds",
    tags=["selection rounds"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_selection_round(
    request: SelectionRoundCreate,
    db: AsyncSession = Depends(get_db),
    reviewer: User = Depends(require_reviewer),
):
    drive_result = await db.execute(
        select(PlacementDrive).where(
            PlacementDrive.id == request.placement_drive_id
        )
    )

    drive = drive_result.scalar_one_or_none()

    if drive is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement drive not found",
        )

    selection_round = SelectionRound(
        placement_drive_id=request.placement_drive_id,
        round_number=request.round_number,
        round_type=request.round_type,
        description=request.description,
    )

    db.add(selection_round)
    await db.commit()
    await db.refresh(selection_round)

    return {
        "message": "Selection round created successfully",
        "selection_round_id": selection_round.id,
        "placement_drive_id": selection_round.placement_drive_id,
        "round_number": selection_round.round_number,
        "round_type": selection_round.round_type,
    }
@router.get(
    "/{placement_drive_id}",
    response_model=list[SelectionRoundResponse],
)
async def get_selection_rounds(
    placement_drive_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SelectionRound)
        .where(
            SelectionRound.placement_drive_id
            == placement_drive_id
        )
        .order_by(SelectionRound.round_number)
    )

    rounds = result.scalars().all()

    return rounds