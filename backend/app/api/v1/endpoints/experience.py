
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.experience import Experience
from app.models.placement_drive import PlacementDrive
from app.models.user import User
from app.schemas.experience import ExperienceCreate
from app.services.experience_intelligence import (
    extract_and_save_claims_for_experience,
)

router = APIRouter(
    prefix="/experiences",
    tags=["Experiences"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_experience(
    request: ExperienceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.verification_status != "VERIFIED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only verified users can submit experiences",
        )

    # Only students and alumni can submit placement experiences.
    if current_user.role not in {"STUDENT", "ALUMNI"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students and alumni can submit experiences",
        )

    drive_result = await db.execute(
        select(PlacementDrive).where(
            PlacementDrive.id == request.placement_drive_id
        )
    )
    placement_drive = drive_result.scalar_one_or_none()

    if placement_drive is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement drive not found",
        )

    experience = Experience(
        user_id=current_user.id,
        placement_drive_id=request.placement_drive_id,
        contributor_type=current_user.role,
        experience_type=request.experience_type,
        content=request.content,
        status="PENDING",
        provenance="SELF_REPORTED",
    )

    db.add(experience)
    await db.commit()
    await db.refresh(experience)

    return experience


@router.get("/pending")
async def get_pending_experiences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "REVIEWER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reviewer access required",
        )

    result = await db.execute(
        select(Experience)
        .where(Experience.status == "PENDING")
        .order_by(Experience.created_at.desc())
    )

    return result.scalars().all()


@router.post("/{experience_id}/approve")
async def approve_experience(
    experience_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "REVIEWER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reviewer access required",
        )

    result = await db.execute(
        select(Experience).where(
            Experience.id == experience_id
        )
    )
    experience = result.scalar_one_or_none()

    if experience is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found",
        )

    if experience.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending experiences can be approved",
        )

    experience.status = "APPROVED"

    await db.commit()
    await db.refresh(experience)

    return experience


@router.post("/{experience_id}/reject")
async def reject_experience(
    experience_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "REVIEWER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reviewer access required",
        )

    result = await db.execute(
        select(Experience).where(
            Experience.id == experience_id
        )
    )
    experience = result.scalar_one_or_none()

    if experience is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found",
        )

    if experience.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending experiences can be rejected",
        )

    experience.status = "REJECTED"

    await db.commit()
    await db.refresh(experience)

    return experience


@router.post("/{experience_id}/extract-claims")
async def extract_claims(
    experience_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "REVIEWER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reviewer access required",
        )

    result = await db.execute(
        select(Experience).where(
            Experience.id == experience_id
        )
    )
    experience = result.scalar_one_or_none()

    if experience is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found",
        )

    if experience.status != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only approved experiences can have claims extracted",
        )

    claims = await extract_and_save_claims_for_experience(
        experience_id,
        db,
    )

    return {
        "experience_id": experience_id,
        "claims": claims,
    }
