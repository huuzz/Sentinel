from collections.abc import AsyncIterator
from typing import Any

from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import OperationalError

from app.db.session import get_session
from app.main import app


async def unavailable_session() -> AsyncIterator[Any]:
    class BrokenSession:
        async def execute(self, _statement: object) -> None:
            raise OperationalError("SELECT 1", {}, Exception("offline"))

    yield BrokenSession()


async def test_liveness() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "sentinelai-backend"}
    assert response.headers["x-request-id"]


async def test_readiness_returns_503_when_database_is_unavailable() -> None:
    app.dependency_overrides[get_session] = unavailable_session
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health/ready")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 503
    assert response.json() == {"detail": "Database is unavailable"}
