
import asyncio
from getpass import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User
from app.db.session import AsyncSessionLocal


async def main():
    email = "reviewer@reva.local"
    new_password = getpass("Enter a new temporary reviewer password: ")

    if len(new_password) < 12:
        print("Use a password with at least 12 characters.")
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if user is None:
            print("Reviewer account not found.")
            return

        user.password_hash = hash_password(new_password)
        await db.commit()

        print("Reviewer password reset successfully.")


if __name__ == "__main__":
    asyncio.run(main())
