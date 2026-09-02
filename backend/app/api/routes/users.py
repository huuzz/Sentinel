import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import AdminUser
from app.core.security import hash_password
from app.db.session import get_session
from app.models.user import AuditLog, User
from app.schemas.auth import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/api/v1/users", tags=["users"])
Session = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[UserResponse])
async def list_users(session: Session, _: AdminUser) -> list[User]:
    return list(await session.scalars(select(User).order_by(User.email)))


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, session: Session, admin: AdminUser) -> User:
    if await session.scalar(select(User.id).where(User.email == payload.email)):
        raise HTTPException(status_code=409, detail="Email already exists")
    user = User(
        email=payload.email, password_hash=hash_password(payload.password), role=payload.role
    )
    session.add(user)
    await session.flush()
    session.add(
        AuditLog(
            actor_user_id=admin.id,
            action="user.create",
            target_type="user",
            target_id=str(user.id),
            outcome="SUCCESS",
            details={"role": user.role.value},
        )
    )
    await session.commit()
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID, payload: UserUpdate, session: Session, admin: AdminUser
) -> User:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id and payload.is_active is False:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    changes = payload.model_dump(exclude_none=True)
    for field, value in changes.items():
        setattr(user, field, value)
    session.add(
        AuditLog(
            actor_user_id=admin.id,
            action="user.update",
            target_type="user",
            target_id=str(user.id),
            outcome="SUCCESS",
            details={key: str(value) for key, value in changes.items()},
        )
    )
    await session.commit()
    return user
