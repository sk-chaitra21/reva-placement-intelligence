
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.claim import Claim
from app.models.claim_embedding import ClaimEmbedding
from app.services.embedding_service import generate_embedding

EMBEDDING_MODEL = "gemini-embedding-2"


def build_claim_text(claim: Claim) -> str:
    """Combine the claim and its supporting evidence for retrieval."""
    parts = [
        f"Claim: {claim.claim_text}",
    ]

    if claim.evidence_text:
        parts.append(f"Supporting evidence: {claim.evidence_text}")

    return "\n".join(parts)


async def create_claim_embedding(
    claim_id: int,
    db: AsyncSession,
):
    result = await db.execute(
        select(Claim).where(Claim.id == claim_id)
    )
    claim = result.scalar_one_or_none()

    if claim is None:
        raise ValueError("Claim not found")

    if claim.verification_status != "VERIFIED":
        raise ValueError("Only verified claims can be embedded")

    text = build_claim_text(claim)
    embedding = await generate_embedding(text)

    existing_result = await db.execute(
        select(ClaimEmbedding).where(
            ClaimEmbedding.claim_id == claim.id
        )
    )
    existing_embedding = existing_result.scalar_one_or_none()

    if existing_embedding:
        existing_embedding.embedding = embedding
        existing_embedding.embedding_model = EMBEDDING_MODEL
    else:
        db.add(
            ClaimEmbedding(
                claim_id=claim.id,
                embedding=embedding,
                embedding_model=EMBEDDING_MODEL,
            )
        )

    await db.commit()

    return {
        "claim_id": claim.id,
        "embedding_dimension": len(embedding),
        "embedding_model": EMBEDDING_MODEL,
    }


async def create_embeddings_for_verified_claims(
    db: AsyncSession,
):
    result = await db.execute(
        select(Claim).where(
            Claim.verification_status == "VERIFIED"
        )
    )
    claims = result.scalars().all()

    embedded_claims = []

    for claim in claims:
        # Create or refresh the embedding for each verified claim.
        embedding_result = await create_claim_embedding(
            claim.id,
            db,
        )
        embedded_claims.append(embedding_result)

    return embedded_claims
