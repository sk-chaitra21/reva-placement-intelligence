
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_reviewer
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.verification_request import VerificationRequest
from app.schemas.verification import VerificationRequestCreate

router = APIRouter(
    prefix="/verification",
    tags=["verification"],
)


@router.post(
    "/request",
    status_code=status.HTTP_201_CREATED,
)
async def create_verification_request(
    request: VerificationRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.verification_status == "VERIFIED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already verified",
        )

    verification_request = VerificationRequest(
        user_id=current_user.id,
        verification_type=request.verification_type,
        institutional_email=request.institutional_email,
        evidence=request.evidence,
        status="PENDING",
    )

    db.add(verification_request)
    await db.commit()
    await db.refresh(verification_request)

    return {
        "message": "Verification request submitted",
        "verification_request_id": verification_request.id,
        "status": verification_request.status,
    }


@router.get("/pending")
async def get_pending_verification_requests(
    db: AsyncSession = Depends(get_db),
    reviewer: User = Depends(require_reviewer),
):
    result = await db.execute(
        select(VerificationRequest).where(
            VerificationRequest.status == "PENDING"
        )
    )

    requests = result.scalars().all()

    return [
        {
            "id": request.id,
            "user_id": request.user_id,
            "verification_type": request.verification_type,
            "institutional_email": request.institutional_email,
            "evidence": request.evidence,
            "status": request.status,
            "created_at": request.created_at,
        }
        for request in requests
    ]


@router.post("/{request_id}/approve")
async def approve_verification_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    reviewer: User = Depends(require_reviewer),
):
    result = await db.execute(
        select(VerificationRequest).where(
            VerificationRequest.id == request_id
        )
    )

    verification_request = result.scalar_one_or_none()

    if verification_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification request not found",
        )

    if verification_request.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification request has already been reviewed",
        )

    user_result = await db.execute(
        select(User).where(
            User.id == verification_request.user_id
        )
    )

    user = user_result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User associated with verification request not found",
        )

    verification_request.status = "VERIFIED"
    verification_request.reviewed_by = reviewer.id
    verification_request.reviewed_at = datetime.now(UTC)

    user.verification_status = "VERIFIED"

    await db.commit()

    return {
        "message": "Verification request approved",
        "verification_request_id": verification_request.id,
        "user_id": user.id,
        "verification_status": user.verification_status,
    }


@router.post("/{request_id}/reject")
async def reject_verification_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    reviewer: User = Depends(require_reviewer),
):
    result = await db.execute(
        select(VerificationRequest).where(
            VerificationRequest.id == request_id
        )
    )

    verification_request = result.scalar_one_or_none()

    if verification_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification request not found",
        )

    if verification_request.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification request has already been reviewed",
        )

    verification_request.status = "REJECTED"
    verification_request.reviewed_by = reviewer.id
    verification_request.reviewed_at = datetime.now(UTC)

    await db.commit()

    return {
        "message": "Verification request rejected",
        "verification_request_id": verification_request.id,
        "status": verification_request.status,
    }
