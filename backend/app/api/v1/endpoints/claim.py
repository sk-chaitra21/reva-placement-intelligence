
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_reviewer
from app.db.session import get_db
from app.models.claim import Claim
from app.models.experience import Experience
from app.models.user import User
from app.schemas.claim import ClaimCreate
from app.services.claim_embedding_service import create_claim_embedding
from app.services.claim_retrieval import retrieve_verified_claims
from app.services.experience_intelligence import (
    extract_and_save_claims_for_experience,
)

router = APIRouter(
    prefix="/claims",
    tags=["claims"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_claim(
    request: ClaimCreate,
    db: AsyncSession = Depends(get_db),
    reviewer: User = Depends(require_reviewer),
):
    experience_result = await db.execute(
        select(Experience).where(
            Experience.id == request.experience_id
        )
    )
    experience = experience_result.scalar_one_or_none()

    if experience is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found",
        )

    if experience.status != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claims can only be created from approved experiences",
        )

    if experience.provenance == "DEMO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claims cannot be created from demo experiences",
        )

    new_claim = Claim(
        experience_id=request.experience_id,
        claim_text=request.claim_text,
        evidence_text=request.evidence_text,
        claim_type=request.claim_type,
        verification_status="PENDING",
    )

    db.add(new_claim)
    await db.commit()
    await db.refresh(new_claim)

    return {
        "message": "Claim created successfully",
        "claim_id": new_claim.id,
        "experience_id": new_claim.experience_id,
        "claim_text": new_claim.claim_text,
        "evidence_text": new_claim.evidence_text,
        "claim_type": new_claim.claim_type,
        "verification_status": new_claim.verification_status,
    }


@router.get("/pending")
async def get_pending_claims(
    db: AsyncSession = Depends(get_db),
    reviewer: User = Depends(require_reviewer),
):
    result = await db.execute(
        select(Claim)
        .join(Experience, Claim.experience_id == Experience.id)
        .where(
            Claim.verification_status == "PENDING",
            Experience.provenance != "DEMO",
        )
        .order_by(Claim.id.desc())
    )

    claims = result.scalars().all()

    return [
        {
            "id": item.id,
            "experience_id": item.experience_id,
            "claim_text": item.claim_text,
            "evidence_text": item.evidence_text,
            "claim_type": item.claim_type,
            "verification_status": item.verification_status,
        }
        for item in claims
    ]


@router.post("/{claim_id}/verify")
async def verify_claim(
    claim_id: int,
    db: AsyncSession = Depends(get_db),
    reviewer: User = Depends(require_reviewer),
):
    result = await db.execute(
        select(Claim).where(Claim.id == claim_id)
    )
    claim = result.scalar_one_or_none()

    if claim is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found",
        )

    if claim.verification_status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending claims can be verified",
        )

    if not claim.evidence_text or not claim.evidence_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claim cannot be verified without supporting evidence",
        )

    experience_result = await db.execute(
        select(Experience).where(
            Experience.id == claim.experience_id
        )
    )
    experience = experience_result.scalar_one_or_none()

    if experience is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked experience not found",
        )

    if experience.provenance == "DEMO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claims from demo experiences cannot be verified",
        )

    if experience.status != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claims can only be verified from approved experiences",
        )

    claim.verification_status = "VERIFIED"
    await db.commit()

    embedding_result = await create_claim_embedding(
        claim_id=claim.id,
        db=db,
    )

    return {
        "message": "Claim verified and embedded successfully",
        "claim_id": claim.id,
        "verification_status": claim.verification_status,
        "embedding": embedding_result,
    }


@router.post("/extract/{experience_id}")
async def extract_experience_claims(
    experience_id: int,
    db: AsyncSession = Depends(get_db),
    reviewer: User = Depends(require_reviewer),
):
    experience_result = await db.execute(
        select(Experience).where(
            Experience.id == experience_id
        )
    )
    experience = experience_result.scalar_one_or_none()

    if experience is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found",
        )

    if experience.status != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claims can only be extracted from approved experiences",
        )

    if experience.provenance == "DEMO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claims cannot be extracted from demo experiences",
        )

    claims = await extract_and_save_claims_for_experience(
        experience_id=experience_id,
        db=db,
    )

    return {
        "message": "Claims extracted and saved successfully",
        "experience_id": experience_id,
        "claims_created": len(claims),
        "claims": [
            {
                "id": item.id,
                "claim_text": item.claim_text,
                "claim_type": item.claim_type,
                "evidence_text": item.evidence_text,
                "verification_status": item.verification_status,
            }
            for item in claims
        ],
    }


@router.get("/verified")
async def get_verified_claims(
    experience_id: int | None = None,
    claim_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    reviewer: User = Depends(require_reviewer),
):
    claims = await retrieve_verified_claims(
        db=db,
        experience_id=experience_id,
        claim_type=claim_type,
    )

    if not claims:
        return []

    # Return only claims linked to non-demo experiences.
    experience_ids = {
        item.experience_id for item in claims
    }

    experience_result = await db.execute(
        select(Experience).where(
            Experience.id.in_(experience_ids),
            Experience.provenance != "DEMO",
            Experience.status == "APPROVED",
        )
    )
    eligible_experience_ids = {
        item.id for item in experience_result.scalars().all()
    }

    return [
        {
            "id": item.id,
            "experience_id": item.experience_id,
            "claim_text": item.claim_text,
            "evidence_text": item.evidence_text,
            "claim_type": item.claim_type,
            "verification_status": item.verification_status,
            "created_at": item.created_at,
        }
        for item in claims
        if item.experience_id in eligible_experience_ids
    ]
