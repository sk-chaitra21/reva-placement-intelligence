
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_reviewer
from app.db.session import get_db
from app.models.eligibility_criteria import EligibilityCriteria
from app.models.placement_drive import PlacementDrive
from app.models.user import User
from app.schemas.eligibility import (
    EligibilityCriteriaCreate,
    EligibilityCriteriaResponse,
)

router = APIRouter(
    prefix="/eligibility",
    tags=["eligibility"],
)


@router.post(
    "/",
    response_model=EligibilityCriteriaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_eligibility_criteria(
    request: EligibilityCriteriaCreate,
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

    existing_result = await db.execute(
        select(EligibilityCriteria).where(
            EligibilityCriteria.placement_drive_id
            == request.placement_drive_id
        )
    )

    if existing_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Eligibility criteria already exist for this placement drive",
        )

    criteria = EligibilityCriteria(**request.model_dump())
    db.add(criteria)
    await db.commit()
    await db.refresh(criteria)

    return criteria


@router.get(
    "/{placement_drive_id}",
    response_model=EligibilityCriteriaResponse,
)
async def get_eligibility_criteria(
    placement_drive_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EligibilityCriteria).where(
            EligibilityCriteria.placement_drive_id == placement_drive_id
        )
    )
    criteria = result.scalar_one_or_none()

    if criteria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Eligibility criteria not found",
        )

    return criteria
