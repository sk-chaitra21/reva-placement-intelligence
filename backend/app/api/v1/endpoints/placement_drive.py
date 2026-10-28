

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_reviewer
from app.db.session import get_db
from app.models.claim import Claim
from app.models.company import Company
from app.models.eligibility_criteria import EligibilityCriteria
from app.models.experience import Experience
from app.models.placement_drive import PlacementDrive
from app.models.selection_round import SelectionRound
from app.models.user import User
from app.schemas.placement_drive import PlacementDriveCreate

router = APIRouter(
    prefix="/placement-drives",
    tags=["placement drives"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_placement_drive(
    request: PlacementDriveCreate,
    db: AsyncSession = Depends(get_db),
    reviewer: User = Depends(require_reviewer),
):
    company_result = await db.execute(
        select(Company).where(
            Company.id == request.company_id
        )
    )
    company = company_result.scalar_one_or_none()

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    duplicate_result = await db.execute(
        select(PlacementDrive).where(
            PlacementDrive.company_id == request.company_id,
            PlacementDrive.academic_year == request.academic_year,
            PlacementDrive.title == request.title,
            PlacementDrive.drive_date == request.drive_date,
        )
    )
    existing_drive = duplicate_result.scalar_one_or_none()

    if existing_drive is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Placement drive already exists",
        )

    placement_drive = PlacementDrive(
        company_id=request.company_id,
        academic_year=request.academic_year,
        drive_date=request.drive_date,
        title=request.title,
        description=request.description,
    )

    db.add(placement_drive)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Placement drive already exists",
        )

    await db.refresh(placement_drive)

    return {
        "message": "Placement drive created successfully",
        "placement_drive_id": placement_drive.id,
        "company_id": placement_drive.company_id,
        "title": placement_drive.title,
    }


@router.get("/{drive_id}/intelligence")
async def get_placement_intelligence(
    drive_id: int,
    db: AsyncSession = Depends(get_db),
):
    # Get placement drive.
    drive_result = await db.execute(
        select(PlacementDrive).where(
            PlacementDrive.id == drive_id
        )
    )
    drive = drive_result.scalar_one_or_none()

    if drive is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement drive not found",
        )

    # Get company.
    company_result = await db.execute(
        select(Company).where(
            Company.id == drive.company_id
        )
    )
    company = company_result.scalar_one_or_none()

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    # Get eligibility criteria.
    eligibility_result = await db.execute(
        select(EligibilityCriteria).where(
            EligibilityCriteria.placement_drive_id == drive_id
        )
    )
    eligibility = eligibility_result.scalar_one_or_none()

    # Get selection rounds.
    rounds_result = await db.execute(
        select(SelectionRound)
        .where(SelectionRound.placement_drive_id == drive_id)
        .order_by(SelectionRound.round_number)
    )
    rounds = rounds_result.scalars().all()

    # Return only approved experiences explicitly marked as non-demo.
    experiences_result = await db.execute(
        select(Experience)
        .where(
            Experience.placement_drive_id == drive_id,
            Experience.status == "APPROVED",
            Experience.provenance != "DEMO",
        )
        .order_by(Experience.created_at.desc())
    )
    experiences = experiences_result.scalars().all()

    # Return only verified claims belonging to approved, non-demo experiences.
    claims_result = await db.execute(
        select(Claim)
        .join(
            Experience,
            Claim.experience_id == Experience.id,
        )
        .where(
            Experience.placement_drive_id == drive_id,
            Experience.status == "APPROVED",
            Experience.provenance != "DEMO",
            Claim.verification_status == "VERIFIED",
        )
        .order_by(Claim.created_at.desc())
    )
    claims = claims_result.scalars().all()

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
            if eligibility is not None
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
                "experience_type": experience.experience_type,
                "content": experience.content,
                "provenance": experience.provenance,
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
            }
            for claim in claims
        ],
    }


@router.get("/search")
async def search_placement_drives(
    company: str | None = None,
    academic_year: str | None = None,
    branch: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(
            PlacementDrive,
            Company,
            EligibilityCriteria,
        )
        .join(
            Company,
            PlacementDrive.company_id == Company.id,
        )
        .outerjoin(
            EligibilityCriteria,
            EligibilityCriteria.placement_drive_id == PlacementDrive.id,
        )
    )

    if company:
        query = query.where(
            Company.name.ilike(f"%{company}%")
        )

    if academic_year:
        query = query.where(
            PlacementDrive.academic_year == academic_year
        )

    if branch:
        query = query.where(
            EligibilityCriteria.eligible_branches.ilike(
                f"%{branch}%"
            )
        )

    query = query.order_by(
        PlacementDrive.academic_year.desc(),
        PlacementDrive.drive_date.desc(),
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        {
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
            "company": {
                "id": company.id,
                "name": company.name,
                "industry": company.industry,
            },
            "eligibility": (
                {
                    "minimum_cgpa": eligibility.minimum_cgpa,
                    "eligible_branches": eligibility.eligible_branches,
                    "graduation_year": eligibility.graduation_year,
                    "backlog_allowed": eligibility.backlog_allowed,
                }
                if eligibility
                else None
            ),
        }
        for drive, company, eligibility in rows
    ]


@router.get("/{drive_id}")
async def get_placement_drive(
    drive_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PlacementDrive).where(
            PlacementDrive.id == drive_id
        )
    )
    drive = result.scalar_one_or_none()

    if drive is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Placement drive not found",
        )

    return {
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
    }
