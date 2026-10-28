from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.user import User


async def require_reviewer(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "REVIEWER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reviewer access required",
        )

    return current_user