import asyncio
from sqlalchemy import text
from app.db.session import engine

async def main():
    async with engine.connect() as connection:
        result = await connection.execute(
            text("SELECT id, placement_drive_id, status, provenance FROM experiences ORDER BY id")
        )
        print(result.fetchall())
    await engine.dispose()

asyncio.run(main())