from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.claim import Claim


async def retrieve_verified_claims(
    db: AsyncSession,
    experience_id: int | None = None,
    claim_type: str | None = None,
):
    query = select(Claim).where(
        Claim.verification_status == "VERIFIED"
    )

    if experience_id is not None:
        query = query.where(
            Claim.experience_id == experience_id
        )

    if claim_type is not None:
        query = query.where(
            Claim.claim_type == claim_type
        )

    query = query.order_by(Claim.created_at.desc())

    result = await db.execute(query)

    return result.scalars().all()