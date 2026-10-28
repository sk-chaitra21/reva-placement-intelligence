
import time

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.intelligence import IntelligenceQuery
from app.services.grounded_answer import generate_grounded_answer
from app.services.vector_retrieval import retrieve_similar_claims

router = APIRouter(
    prefix="/intelligence",
    tags=["Intelligence"],
)


@router.post("/query")
async def query_intelligence(
    request: IntelligenceQuery,
    db: AsyncSession = Depends(get_db),
):
    total_start = time.perf_counter()
    retrieval_start = time.perf_counter()

    claims = await retrieve_similar_claims(
        question=request.question,
        db=db,
        limit=min(request.limit, 3),
        demo_mode=request.demo_mode,
    )

    retrieval_time = time.perf_counter() - retrieval_start

    if not claims:
        total_time = time.perf_counter() - total_start
        print(
            f"[RAG] retrieval={retrieval_time:.2f}s "
            f"generation=0.00s total={total_time:.2f}s"
        )

        return {
            "question": request.question,
            "answer": (
                "No sufficiently relevant "
                + ("approved demo records were found." if request.demo_mode
                   else "verified non-demo placement evidence was found.")
            ),
            "is_demo_data": request.demo_mode,
            "notice": (
                "DEMO MODE: Results, when available, use fictional test "
                "records and do not represent real REVA placement outcomes."
                if request.demo_mode
                else None
            ),
            "sources": [],
        }

    # Defense in depth: enforce the requested provenance mode.
    has_demo_source = any(
        source.get("source", {}).get("provenance") == "DEMO"
        for source in claims
    )

    if has_demo_source != request.demo_mode:
        return {
            "question": request.question,
            "answer": "The retrieved records did not match the requested evidence mode.",
            "is_demo_data": False,
            "notice": None,
            "sources": [],
        }

    generation_start = time.perf_counter()

    answer = await generate_grounded_answer(
        question=request.question,
        retrieved_claims=claims,
    )

    generation_time = time.perf_counter() - generation_start
    total_time = time.perf_counter() - total_start

    print(
        f"[RAG] retrieval={retrieval_time:.2f}s "
        f"generation={generation_time:.2f}s total={total_time:.2f}s"
    )

    return {
        "question": request.question,
        "answer": answer,
        "is_demo_data": request.demo_mode,
        "notice": (
            "DEMO DATA ONLY: These are fictional test records, not real "
            "placement outcomes."
            if request.demo_mode
            else None
        ),
        "sources": claims,
    }
