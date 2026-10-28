from google import genai

from app.core.config import settings

client = genai.Client(
    api_key=settings.gemini_api_key,
)


async def generate_embedding(text: str) -> list[float]:
    response = await client.aio.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
        config={
            "output_dimensionality": 768,
        },
    )

    if not response.embeddings:
        raise ValueError("Gemini returned no embedding.")

    return response.embeddings[0].values