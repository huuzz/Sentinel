import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import CurrentUser
from app.core.config import Settings, get_settings
from app.core.security import create_access_token, new_refresh_token, token_hash, verify_password
from app.db.session import get_session
from app.models.user import AuditLog, RefreshToken, User
from app.schemas.auth import AccessTokenResponse, LoginRequest, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
Session = Annotated[AsyncSession, Depends(get_session)]
Config = Annotated[Settings, Depends(get_settings)]
REFRESH_COOKIE = "sentinel_refresh"


def set_refresh_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        REFRESH_COOKIE,
        token,
        max_age=settings.refresh_token_days * 86400,
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite="strict",
        path="/api/v1/auth",
    )


async def issue_session(
    session: AsyncSession,
    user: User,
    settings: Settings,
    response: Response,
    family_id: uuid.UUID | None = None,
) -> tuple[AccessTokenResponse, str]:
    raw = new_refresh_token()
    session.add(
        RefreshToken(
            user_id=user.id,
            family_id=family_id or uuid.uuid4(),
            token_hash=token_hash(raw),
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_days),
        )
    )
    set_refresh_cookie(response, raw, settings)
    return AccessTokenResponse(
        access_token=create_access_token(user.id, user.role.value, settings),
        expires_in=settings.access_token_minutes * 60,
    ), token_hash(raw)


@router.post("/login", response_model=AccessTokenResponse)
async def login(
    payload: LoginRequest, response: Response, session: Session, settings: Config
) -> AccessTokenResponse:
    user = await session.scalar(select(User).where(User.email == payload.email.lower()))
    if (
        user is None
        or not user.is_active
        or not verify_password(user.password_hash, payload.password)
    ):
        session.add(
            AuditLog(
                actor_user_id=user.id if user else None,
                action="auth.login",
                outcome="FAILURE",
                details={"email": payload.email.lower()},
            )
        )
        await session.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    result, _ = await issue_session(session, user, settings, response)
    session.add(AuditLog(actor_user_id=user.id, action="auth.login", outcome="SUCCESS"))
    await session.commit()
    return result


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(
    response: Response,
    session: Session,
    settings: Config,
    sentinel_refresh: Annotated[str | None, Cookie()] = None,
) -> AccessTokenResponse:
    if not sentinel_refresh:
        raise HTTPException(status_code=401, detail="Refresh token required")
    digest = token_hash(sentinel_refresh)
    record = await session.scalar(select(RefreshToken).where(RefreshToken.token_hash == digest))
    if record is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if record.revoked_at is not None:
        await session.execute(
            update(RefreshToken)
            .where(RefreshToken.family_id == record.family_id)
            .values(revoked_at=datetime.now(UTC))
        )
        await session.commit()
        response.delete_cookie(REFRESH_COOKIE, path="/api/v1/auth")
        raise HTTPException(status_code=401, detail="Refresh token reuse detected")
    if record.expires_at <= datetime.now(UTC):
        raise HTTPException(status_code=401, detail="Refresh token expired")
    user = await session.get(User, record.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User unavailable")
    record.revoked_at = datetime.now(UTC)
    result, replacement_hash = await issue_session(
        session, user, settings, response, record.family_id
    )
    record.replaced_by_hash = replacement_hash
    await session.commit()
    return result


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    session: Session,
    user: CurrentUser,
    sentinel_refresh: Annotated[str | None, Cookie()] = None,
) -> None:
    if sentinel_refresh:
        record = await session.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash(sentinel_refresh))
        )
        if record:
            await session.execute(
                update(RefreshToken)
                .where(
                    RefreshToken.family_id == record.family_id, RefreshToken.revoked_at.is_(None)
                )
                .values(revoked_at=datetime.now(UTC))
            )
    session.add(AuditLog(actor_user_id=user.id, action="auth.logout", outcome="SUCCESS"))
    await session.commit()
    response.delete_cookie(REFRESH_COOKIE, path="/api/v1/auth")


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser) -> User:
    return user
