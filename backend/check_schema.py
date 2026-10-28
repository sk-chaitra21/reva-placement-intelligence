import asyncio
from sqlalchemy import text
from app.db.session import engine


async def main():
    async with engine.connect() as connection:
        result = await connection.execute(
            text("""
                SELECT column_name, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'claim_embeddings'
                  AND column_name = 'created_at'
            """)
        )
        print("created_at column:", result.fetchall())

        result = await connection.execute(
            text("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'claim_embeddings'
            """)
        )
        print("Indexes:", result.fetchall())

    await engine.dispose()


asyncio.run(main())