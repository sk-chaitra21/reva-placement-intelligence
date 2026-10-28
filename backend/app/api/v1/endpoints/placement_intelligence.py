
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.claim import Claim
from app.models.company import Company
from app.models.eligibility_criteria import EligibilityCriteria
from app.models.experience import Experience
from app.models.placement_drive import PlacementDrive
from app.models.selection_round import SelectionRound
from app.schemas.placement_intelligence import (
    PlacementIntelligenceResponse,
)

router = APIRouter(
    prefix="/placement-drives",
    tags=["Placement Intelligence"],
)


@router.get(
    "/{drive_id}/intelligence",
    response_model=PlacementIntelligenceResponse,
)
async def get_placement_intelligence(
    drive_id: int,
    db: AsyncSession = Depends(get_db),
):
    # 1. Get placement drive
    drive_result = await db.execute(
        select(PlacementDrive).where(
            PlacementDrive.id == drive_id
        )
    )
    drive = drive_result.scalar_one_or_none()

    if drive is None:
        raise HTTPException(
            status_code=404,
            detail="Placement drive not found",
        )

    # 2. Get company
    company_result = await db.execute(
        select(Company).where(
            Company.id == drive.company_id
        )
    )
    company = company_result.scalar_one_or_none()

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    # 3. Get eligibility criteria
    eligibility_result = await db.execute(
        select(EligibilityCriteria).where(
            EligibilityCriteria.placement_drive_id == drive_id
        )
    )
    eligibility = eligibility_result.scalar_one_or_none()

    # 4. Get selection rounds
    rounds_result = await db.execute(
        select(SelectionRound)
        .where(SelectionRound.placement_drive_id == drive_id)
        .order_by(SelectionRound.round_number)
    )
    rounds = rounds_result.scalars().all()

    # 5. Get approved experiences
    experiences_result = await db.execute(
        select(Experience)
        .where(
            Experience.placement_drive_id == drive_id,
            Experience.status == "APPROVED",
        )
        .order_by(Experience.created_at.desc())
    )
    experiences = experiences_result.scalars().all()

    # Build a lookup for experience details
    experience_by_id = {
        experience.id: experience
        for experience in experiences
    }

    # 6. Get verified claims from approved experiences
    claims_result = await db.execute(
        select(Claim)
        .join(
            Experience,
            Claim.experience_id == Experience.id,
        )
        .where(
            Experience.placement_drive_id == drive_id,
            Experience.status == "APPROVED",
            Claim.verification_status == "VERIFIED",
        )
        .order_by(Claim.created_at.desc())
    )
    claims = claims_result.scalars().all()

    # 7. Return combined placement intelligence
    return {
        "company": {
            "id": company.id,
            "name": company.name,
            "industry": company.industry,
            "description": company.description,
            "website": company.website,
        },
        "placement_drive": {
            "id": drive.id,
            "company_id": drive.company_id,
            "academic_year": drive.academic_year,
            "drive_date": (
                drive.drive_date.isoformat()
                if drive.drive_date
                else None
            ),
            "title": drive.title,
            "description": drive.description,
        },
        "eligibility": (
            {
                "id": eligibility.id,
                "placement_drive_id": eligibility.placement_drive_id,
                "minimum_cgpa": eligibility.minimum_cgpa,
                "eligible_branches": eligibility.eligible_branches,
                "graduation_year": eligibility.graduation_year,
                "backlog_allowed": eligibility.backlog_allowed,
                "other_criteria": eligibility.other_criteria,
            }
            if eligibility
            else None
        ),
        "selection_rounds": [
            {
                "id": selection_round.id,
                "placement_drive_id": selection_round.placement_drive_id,
                "round_number": selection_round.round_number,
                "round_type": selection_round.round_type,
                "description": selection_round.description,
            }
            for selection_round in rounds
        ],
        "verified_experiences": [
            {
                "id": experience.id,
                "contributor_type": experience.contributor_type,
                "content": experience.content,
            }
            for experience in experiences
        ],
        "verified_claims": [
            {
                "id": claim.id,
                "experience_id": claim.experience_id,
                "claim_text": claim.claim_text,
                "evidence_text": claim.evidence_text,
                "claim_type": claim.claim_type,
                "verification_status": claim.verification_status,
                "contributor_type": (
                    experience_by_id[claim.experience_id].contributor_type
                ),
                "company": company.name,
                "academic_year": drive.academic_year,
                "placement_drive": drive.title,
            }
            for claim in claims
            if claim.experience_id in experience_by_id
        ],
    }
