import re
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from ipaddress import ip_address
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.api.routes.alerts import router as alerts_router
from app.api.routes.analysis import router as analysis_router
from app.api.routes.audit import router as audit_router
from app.api.routes.auth import router as auth_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.events import router as events_router
from app.api.routes.health import router as health_router
from app.api.routes.knowledge import router as knowledge_router
from app.api.routes.ml import router as ml_router
from app.api.routes.users import router as users_router
from app.core.config import get_settings
from app.core.hardening import BodySizeLimitMiddleware, rate_limiter
from app.core.logging import configure_logging
from app.db.session import close_engine
from app.ml.runtime import ml_runtime

settings = get_settings()
configure_logging(settings)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    if settings.ml_enabled:
        ml_runtime.load(settings.ml_model_path)
    yield
    await close_engine()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(BodySizeLimitMiddleware, max_bytes=settings.max_request_body_bytes)
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(audit_router)
app.include_router(events_router)
app.include_router(alerts_router)
app.include_router(analysis_router)
app.include_router(ml_router)
app.include_router(knowledge_router)
app.include_router(dashboard_router)


@app.middleware("http")
async def request_context(request: Request, call_next: Any) -> Any:
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,64}", request_id):
        request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    if request.method in {"POST", "PUT", "PATCH"}:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                declared_size = int(content_length)
            except ValueError:
                return error_response(
                    400, "invalid_content_length", "Invalid Content-Length", request_id
                )
            if declared_size > settings.max_request_body_bytes:
                return error_response(
                    413, "request_too_large", "Request body is too large", request_id
                )

    rate = rate_policy(request.method, request.url.path)
    if rate is not None:
        category, limit = rate
        client_ip = trusted_client_ip(request)
        allowed, retry_after = await rate_limiter.allow(
            f"{category}:{client_ip}", limit, settings.rate_limit_window_seconds
        )
        if not allowed:
            response = error_response(429, "rate_limited", "Too many requests", request_id)
            response.headers["Retry-After"] = str(retry_after)
            return response
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path not in {"/docs", "/redoc", "/docs/oauth2-redirect"}:
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    if settings.environment == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response


def error_response(status_code: int, code: str, message: str, request_id: str) -> JSONResponse:
    response = JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "request_id": request_id}},
    )
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


def trusted_client_ip(request: Request) -> str:
    peer = request.client.host if request.client else "unknown"
    if peer in settings.trusted_proxies:
        forwarded = request.headers.get("x-forwarded-for", "").strip()
        try:
            return str(ip_address(forwarded))
        except ValueError:
            pass  # Trusted proxies must overwrite, not append, the client address.
    return peer


def rate_policy(method: str, path: str) -> tuple[str, int] | None:
    if method == "POST" and path in {"/api/v1/auth/login", "/api/v1/auth/refresh"}:
        return "auth", settings.auth_rate_limit
    if method == "POST" and path == "/api/v1/events":
        return "ingestion", settings.ingestion_rate_limit
    if method == "POST" and (path.endswith("/analysis") or path == "/api/v1/knowledge/ask"):
        return "ai", settings.ai_rate_limit
    if method in {"POST", "PATCH", "DELETE"} and (
        path.startswith("/api/v1/users") or path == "/api/v1/knowledge/entries"
    ):
        return "admin", settings.admin_rate_limit
    return None


@app.exception_handler(Exception)
async def unhandled_exception(request: Request, _: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "An unexpected error occurred",
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, error: RequestValidationError) -> JSONResponse:
    # Return field locations and error types only; submitted values may be sensitive.
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "request_id": getattr(request.state, "request_id", None),
                "fields": [
                    {"location": list(item["loc"]), "type": item["type"]} for item in error.errors()
                ],
            }
        },
    )
