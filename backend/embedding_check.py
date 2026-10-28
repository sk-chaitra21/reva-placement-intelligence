import asyncio

from app.db.session import AsyncSessionLocal
from app.services.claim_embedding_service import (
    create_embeddings_for_verified_claims,
)


async def main():
    async with AsyncSessionLocal() as db:
        result = await create_embeddings_for_verified_claims(db)
        print(result)


asyncio.run(main())