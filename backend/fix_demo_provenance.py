import asyncio
from sqlalchemy import text
from app.db.session import engine


async def main():
    async with engine.begin() as connection:
        result = await connection.execute(
            text("""
                UPDATE experiences
                SET provenance = 'DEMO'
                WHERE id = 6
                  AND content LIKE '%Demo experience for testing%'
            """)
        )
        print(f"Records updated: {result.rowcount}")

    await engine.dispose()


asyncio.run(main())