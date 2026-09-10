import argparse
import asyncio
import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionFactory, close_engine
from app.models.user import AuditLog, User, UserRole


async def create_admin(email: str, password: str) -> None:
    normalized = email.strip().lower()
    async with SessionFactory() as session:
        if await session.scalar(select(User.id).where(User.email == normalized)):
            raise SystemExit("A user with that email already exists")
        user = User(email=normalized, password_hash=hash_password(password), role=UserRole.ADMIN)
        session.add(user)
        await session.flush()
        session.add(
            AuditLog(
                actor_user_id=user.id,
                action="user.bootstrap_admin",
                target_type="user",
                target_id=str(user.id),
                outcome="SUCCESS",
            )
        )
        await session.commit()
    print(f"Created admin {normalized}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the first Sentinel administrator")
    parser.add_argument("--email", required=True)
    args = parser.parse_args()
    password = getpass.getpass("Password (12+ characters): ").rstrip("\r\n")
    if len(password) < 12:
        raise SystemExit("Password must contain at least 12 characters")

    async def run() -> None:
        try:
            await create_admin(args.email, password)
        finally:
            await close_engine()

    asyncio.run(run())


if __name__ == "__main__":
    main()
