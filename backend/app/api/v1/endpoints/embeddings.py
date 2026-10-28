from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.claim_embedding_service import create_claim_embedding

router = APIRouter(
    prefix="/embeddings",
    tags=["Embeddings"],
)


@router.post("/claims/{claim_id}")
async def create_embedding_for_claim(
    claim_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "REVIEWER":
        raise HTTPException(
            status_code=403,
            detail="Reviewer access required",
        )

    try:
        result = await create_claim_embedding(
            claim_id=claim_id,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return result