from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.claim import Claim
from app.models.experience import Experience
from app.services.claim_extraction import extract_claims_from_experience


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


async def extract_and_save_claims_for_experience(
    experience_id: int,
    db: AsyncSession,
):
    result = await db.execute(
        select(Experience).where(
            Experience.id == experience_id
        )
    )

    experience = result.scalar_one_or_none()

    if experience is None:
        raise HTTPException(
            status_code=404,
            detail="Experience not found",
        )

    if experience.status != "APPROVED":
        raise HTTPException(
            status_code=400,
            detail="Claims can only be extracted from approved experiences",
        )

    # Get claims already extracted for this experience
    existing_result = await db.execute(
        select(Claim).where(
            Claim.experience_id == experience.id
        )
    )

    existing_claims = existing_result.scalars().all()

    existing_evidence = {
        normalize_text(claim.evidence_text)
        for claim in existing_claims
        if claim.evidence_text
    }

    extraction_result = await extract_claims_from_experience(
        experience.content
    )

    saved_claims = []

    for extracted_claim in extraction_result.claims:
        normalized_evidence = normalize_text(
            extracted_claim.evidence_text
        )

        # Skip duplicate claims based on evidence
        if normalized_evidence in existing_evidence:
            continue

        claim = Claim(
            experience_id=experience.id,
            claim_text=extracted_claim.claim_text,
            claim_type=extracted_claim.claim_type,
            evidence_text=extracted_claim.evidence_text,
            verification_status="PENDING",
        )

        db.add(claim)
        saved_claims.append(claim)

        existing_evidence.add(normalized_evidence)

    await db.commit()

    for claim in saved_claims:
        await db.refresh(claim)

    return saved_claims