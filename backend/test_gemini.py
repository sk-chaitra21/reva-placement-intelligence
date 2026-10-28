
import asyncio
from app.ai.gemini import client


async def main():
    print("Testing Gemini connection...")

    try:
        response = await client.aio.interactions.create(
            model="gemini-3.6-flash",
            input="Reply with exactly: Gemini connection works.",
        )
        print("Gemini response:")
        print(response.output_text)

    except Exception as exc:
        print("Gemini test failed:")
        print(type(exc).__name__)
        print(str(exc))


if __name__ == "__main__":
    asyncio.run(main())
