import asyncio
from collections.abc import AsyncIterator

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from app import main
from app.api.dependencies import get_current_user, require_roles
from app.core.config import Settings
from app.core.hardening import SlidingWindowRateLimiter
from app.main import rate_policy
from app.models.user import User, UserRole


def test_rate_limiter_rejects_after_limit() -> None:
    limiter = SlidingWindowRateLimiter()

    async def exercise() -> None:
        assert await limiter.allow("auth:example", 2, 60) == (True, 0)
        assert await limiter.allow("auth:example", 2, 60) == (True, 0)
        allowed, retry_after = await limiter.allow("auth:example", 2, 60)
        assert allowed is False
        assert retry_after > 0

    asyncio.run(exercise())


def test_sensitive_routes_have_rate_policies() -> None:
    policies = [
        rate_policy("POST", "/api/v1/auth/login"),
        rate_policy("POST", "/api/v1/events"),
        rate_policy("POST", "/api/v1/alerts/example/analysis"),
        rate_policy("POST", "/api/v1/users"),
    ]
    assert [policy[0] for policy in policies if policy] == ["auth", "ingestion", "ai", "admin"]
    assert rate_policy("GET", "/health/live") is None


async def test_chunked_body_cannot_bypass_limit() -> None:
    async def chunks() -> AsyncIterator[bytes]:
        for _ in range(3):
            yield b"x" * 524_288

    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as client:
        response = await client.post("/api/v1/auth/login", content=chunks())
    assert response.status_code == 413


async def test_http_rate_limit_and_retry_header(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main, "rate_limiter", SlidingWindowRateLimiter())
    monkeypatch.setattr(main.settings, "auth_rate_limit", 1)
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as client:
        first = await client.post("/api/v1/auth/refresh")
        second = await client.post("/api/v1/auth/refresh", headers={"X-Forwarded-For": "192.0.2.9"})
    assert first.status_code == 401
    assert second.status_code == 429
    assert int(second.headers["retry-after"]) > 0
    assert second.json()["error"]["request_id"]


def test_production_rejects_insecure_defaults() -> None:
    with pytest.raises(ValidationError):
        Settings(environment="production", refresh_cookie_secure=False)
    with pytest.raises(ValidationError):
        Settings(trusted_proxy_ips="*")


async def test_validation_never_echoes_password() -> None:
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login", json={"email": "invalid", "password": "secret"}
        )
    assert response.status_code == 422
    assert "secret" not in response.text
    assert response.json()["error"]["code"] == "validation_error"


@pytest.mark.parametrize("role", list(UserRole))
@pytest.mark.parametrize("permission", ["read", "investigate", "admin"])
async def test_role_permission_matrix(role: UserRole, permission: str) -> None:
    allowed = {
        "read": (UserRole.ADMIN, UserRole.ANALYST, UserRole.VIEWER),
        "investigate": (UserRole.ADMIN, UserRole.ANALYST),
        "admin": (UserRole.ADMIN,),
    }[permission]
    user = User(email="test@example.com", password_hash="unused", role=role)
    dependency = require_roles(*allowed)
    if role in allowed:
        assert await dependency(user) is user
    else:
        with pytest.raises(HTTPException) as error:
            await dependency(user)
        assert error.value.status_code == 403


@pytest.mark.parametrize(
    "method,path,role",
    [
        ("POST", "/api/v1/events", UserRole.VIEWER),
        ("PATCH", "/api/v1/alerts/00000000-0000-0000-0000-000000000001", UserRole.VIEWER),
        ("POST", "/api/v1/alerts/00000000-0000-0000-0000-000000000001/analysis", UserRole.VIEWER),
        ("POST", "/api/v1/users", UserRole.ANALYST),
        ("POST", "/api/v1/users", UserRole.VIEWER),
        ("POST", "/api/v1/knowledge/entries", UserRole.ANALYST),
        ("POST", "/api/v1/knowledge/entries", UserRole.VIEWER),
        ("GET", "/api/v1/audit-logs", UserRole.VIEWER),
    ],
)
async def test_protected_route_denial(method: str, path: str, role: UserRole) -> None:
    async def current_user() -> User:
        return User(email="test@example.com", password_hash="unused", role=role)

    main.app.dependency_overrides[get_current_user] = current_user
    try:
        async with AsyncClient(
            transport=ASGITransport(app=main.app), base_url="http://test"
        ) as client:
            response = await client.request(method, path, json={})
        assert response.status_code == 403
    finally:
        main.app.dependency_overrides.pop(get_current_user, None)
