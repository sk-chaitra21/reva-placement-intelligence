
import asyncio
import logging

from fastapi import HTTPException
from google.genai.errors import APIError

from app.ai.gemini import client
from app.schemas.ai import ClaimExtractionResult

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-3.6-flash"
REQUEST_TIMEOUT_SECONDS = 30


async def extract_claims_from_experience(
    experience_text: str,
) -> ClaimExtractionResult:
    prompt = f"""
You are extracting structured placement knowledge from a student's
placement experience.

Extract only claims that are explicitly supported by the experience text.

For each claim provide:
- claim_text
- claim_type
- evidence_text

Rules:
- Do not invent facts.
- Do not add information that is not present.
- evidence_text must be an exact supporting sentence or phrase from
  the experience text.
- Keep claims concise.
- Focus on placement process, selection rounds, preparation,
  skills, interview experience, and outcomes.

Experience:
{experience_text}
"""

    try:
        interaction = await asyncio.wait_for(
            client.aio.interactions.create(
                model=MODEL_NAME,
                input=prompt,
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": ClaimExtractionResult.model_json_schema(),
                },
            ),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        return ClaimExtractionResult.model_validate_json(
            interaction.output_text
        )

    except TimeoutError as exc:
        logger.warning("Gemini claim extraction timed out")
        raise HTTPException(
            status_code=504,
            detail="Claim extraction timed out. Please try again later.",
        ) from exc

    except APIError as exc:
        status_code = getattr(exc, "code", None)

        logger.warning(
            "Gemini API error during claim extraction: status=%s",
            status_code,
        )

        if status_code == 429:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Gemini quota or rate limit reached. "
                    "Please wait for quota availability before retrying."
                ),
            ) from exc

        raise HTTPException(
            status_code=502,
            detail="The Gemini service could not complete claim extraction.",
        ) from exc

    except (ValueError, TypeError) as exc:
        logger.exception("Invalid Gemini claim extraction response")
        raise HTTPException(
            status_code=502,
            detail="Gemini returned an invalid claim extraction response.",
        ) from exc
