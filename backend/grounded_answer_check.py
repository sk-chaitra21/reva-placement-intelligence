import asyncio

from app.db.session import AsyncSessionLocal
from app.services.vector_retrieval import retrieve_similar_claims
from app.services.grounded_answer import generate_grounded_answer


async def main():
    question = "What should I prepare for placement interviews?"

    async with AsyncSessionLocal() as db:
        claims = await retrieve_similar_claims(
            question,
            db,
            limit=3,
        )

        answer = await generate_grounded_answer(
            question,
            claims,
        )

        print("\n--- RETRIEVED CLAIMS ---")

        for claim in claims:
            print(claim)

        print("\n--- GROUNDED ANSWER ---")
        print(answer)


asyncio.run(main())