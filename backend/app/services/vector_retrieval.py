
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.claim import Claim
from app.models.claim_embedding import ClaimEmbedding
from app.models.company import Company
from app.models.experience import Experience
from app.models.placement_drive import PlacementDrive
from app.services.embedding_service import generate_embedding


async def retrieve_similar_claims(
    question: str,
    db: AsyncSession,
    limit: int = 5,
    min_similarity: float = 0.70,
    demo_mode: bool = False,
) -> list[dict]:
    query_embedding = await generate_embedding(question)

    distance = ClaimEmbedding.embedding.cosine_distance(
        query_embedding
    )

    provenance_filter = (
        Experience.provenance == "DEMO"
        if demo_mode
        else Experience.provenance != "DEMO"
    )

    query = (
        select(
            Claim,
            Experience,
            PlacementDrive,
            Company,
            distance.label("distance"),
        )
        .join(ClaimEmbedding, Claim.id == ClaimEmbedding.claim_id)
        .join(Experience, Claim.experience_id == Experience.id)
        .join(
            PlacementDrive,
            Experience.placement_drive_id == PlacementDrive.id,
        )
        .join(Company, PlacementDrive.company_id == Company.id)
        .where(
            Claim.verification_status == "VERIFIED",
            Experience.status == "APPROVED",
            provenance_filter,
            distance <= (1 - min_similarity),
        )
        .order_by(distance)
        .limit(max(1, min(limit, 3)))
    )

    result = await db.execute(query)
    rows = result.all()

    sources = []

    for claim, experience, placement_drive, company, raw_distance in rows:
        if raw_distance is None:
            continue

        is_demo = experience.provenance == "DEMO"

        sources.append(
            {
                "claim_id": claim.id,
                "claim_text": claim.claim_text,
                "evidence_text": claim.evidence_text or "",
                "claim_type": claim.claim_type,
                "similarity": 1 - float(raw_distance),
                "is_demo_data": is_demo,
                "source": {
                    "experience_id": experience.id,
                    "contributor_type": experience.contributor_type,
                    "provenance": experience.provenance,
                    "company": company.name,
                    "academic_year": placement_drive.academic_year,
                    "placement_drive": placement_drive.title,
                    "data_label": (
                        "DEMO DATA — FICTIONAL TEST RECORDS"
                        if is_demo
                        else "Reported placement experience — verify source"
                    ),
                },
            }
        )

    return sources
