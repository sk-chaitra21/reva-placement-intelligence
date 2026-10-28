
import asyncio
import logging

from google import genai
from google.genai import errors

from app.core.config import settings

logger = logging.getLogger(__name__)

client = genai.Client(
    api_key=settings.gemini_api_key,
)

MODEL_NAME = "gemini-3.6-flash"
MAX_ATTEMPTS = 3


async def generate_grounded_answer(
    question: str,
    retrieved_claims: list[dict],
) -> str:
    if not retrieved_claims:
        return (
            "The available placement evidence is insufficient "
            "to answer this confidently."
        )

    is_demo_data = any(
        claim.get("is_demo_data", False)
        or claim.get("source", {}).get("data_label", "").startswith("DEMO DATA")
        for claim in retrieved_claims
    )

    if is_demo_data:
        evidence_label = "Fictional demo examples (not real placement records)"
        evidence_phrase = "In these demo examples"
        grounding_rules = """
- These are fictional or test records, NOT genuine REVA placement evidence.
- Never call these records "verified placement evidence" or imply they
  represent actual student outcomes.
- Describe findings as "In these demo examples..." or
  "The sample records mention...".
- Make no claims about actual REVA placement practices or company outcomes.
"""
    else:
        evidence_label = "Verified evidence from reported placement experiences"
        evidence_phrase = "In the reported experience"
        grounding_rules = """
- Describe claims as reported experiences, not universal rules or guarantees.
- Use "In the reported experience..." where appropriate.
"""

    evidence = "\n\n".join(
        f"Claim: {claim['claim_text']}\n"
        f"Evidence: {claim['evidence_text']}\n"
        f"Source company: {claim['source']['company']}\n"
        f"Academic year: {claim['source']['academic_year']}\n"
        f"Contributor type: {claim['source']['contributor_type']}\n"
        f"Placement drive: {claim['source']['placement_drive']}"
        for claim in retrieved_claims
    )

    prompt = f"""
You are the placement intelligence assistant for REVA University.

Answer the student's question using ONLY the evidence below.

IMPORTANT GROUNDING RULES:
- Do not invent facts or use outside knowledge.
- Do not turn one experience into a universal placement rule.
- Do not use "typically", "always", "usually", or "all" unless supported.
- If evidence is insufficient, state that clearly.
- Do not make unsupported claims about eligibility, selection rounds,
  salaries, companies, or placement outcomes.
- Keep the answer concise, readable, and useful.
- Use Markdown headings or bullet points when helpful.
{grounding_rules}

Evidence category: {evidence_label}
Preferred phrasing: {evidence_phrase}

Student question:
{question}

Available evidence:
{evidence}
"""

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = await client.aio.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            answer = response.text

            if answer and answer.strip():
                return answer.strip()

            logger.warning(
                "Gemini returned an empty answer (attempt %s/%s).",
                attempt + 1,
                MAX_ATTEMPTS,
            )

        except errors.ServerError as exc:
            logger.warning(
                "Gemini server error on attempt %s/%s: %s",
                attempt + 1,
                MAX_ATTEMPTS,
                exc,
            )

        except errors.APIError as exc:
            if exc.code not in (408, 429):
                logger.exception("Gemini API request failed.")
                return (
                    "Placement intelligence is temporarily unavailable. "
                    "Please try again later."
                )

            logger.warning(
                "Temporary Gemini API error on attempt %s/%s: %s",
                attempt + 1,
                MAX_ATTEMPTS,
                exc,
            )

        if attempt < MAX_ATTEMPTS - 1:
            await asyncio.sleep(1.5 * (attempt + 1))

    logger.error("Gemini answer generation failed after all attempts.")

    return (
        "The evidence was retrieved, but the answer service is temporarily "
        "unavailable. Please try again shortly."
    )
