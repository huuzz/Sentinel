import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes.alerts import router as alerts_router
from app.api.routes.analysis import router as analysis_router
from app.api.routes.audit import router as audit_router
from app.api.routes.auth import router as auth_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.events import router as events_router
from app.api.routes.health import router as health_router
from app.api.routes.ml import router as ml_router
from app.api.routes.users import router as users_router
from app.core.config import get_settings
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
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(audit_router)
app.include_router(events_router)
app.include_router(alerts_router)
app.include_router(analysis_router)
app.include_router(ml_router)
app.include_router(dashboard_router)


@app.middleware("http")
async def request_context(request: Request, call_next: Any) -> Any:
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


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
