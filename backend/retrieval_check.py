import asyncio

from app.db.session import AsyncSessionLocal
from app.services.vector_retrieval import retrieve_similar_claims


async def main():
    question = "What should I prepare for placement interviews?"

    async with AsyncSessionLocal() as db:
        results = await retrieve_similar_claims(
            question,
            db,
            limit=5,
        )

        for result in results:
            print(result)


asyncio.run(main())