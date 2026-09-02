import uuid
from collections.abc import Awaitable, Callable
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.security import decode_access_token
from app.db.session import get_session
from app.models.user import User, UserRole

bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise error
    try:
        payload = decode_access_token(credentials.credentials, settings)
        if payload.get("type") != "access":
            raise error
        user = await session.get(User, uuid.UUID(payload["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError):
        raise error from None
    if user is None or not user.is_active:
        raise error
    # Authorization lookup must not leave an implicit read transaction open for use cases
    # that establish their own explicit transaction boundary.
    await session.commit()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole) -> Callable[[User], Awaitable[User]]:
    async def dependency(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return dependency


ViewerUser = Annotated[
    User, Depends(require_roles(UserRole.VIEWER, UserRole.ANALYST, UserRole.ADMIN))
]
AnalystUser = Annotated[User, Depends(require_roles(UserRole.ANALYST, UserRole.ADMIN))]
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
