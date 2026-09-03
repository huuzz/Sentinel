from fastapi import APIRouter
from pydantic import BaseModel

from app.api.dependencies import ViewerUser
from app.ml.features import FEATURE_SCHEMA_VERSION
from app.ml.runtime import ml_runtime

router = APIRouter(prefix="/api/v1/ml", tags=["ml"])


class MLStatus(BaseModel):
    available: bool
    model_version: str | None
    feature_schema_version: str
    detail: str


@router.get("/status", response_model=MLStatus)
async def ml_status(_: ViewerUser) -> MLStatus:
    return MLStatus(
        available=ml_runtime.available,
        model_version=ml_runtime.model_version,
        feature_schema_version=FEATURE_SCHEMA_VERSION,
        detail="advisory only" if ml_runtime.available else (ml_runtime.error or "unavailable"),
    )
