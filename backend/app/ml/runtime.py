import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib  # type: ignore[import-untyped]
import numpy as np

from app.ml.features import FEATURE_NAMES, FEATURE_SCHEMA_VERSION, extract_features
from app.models.security_event import SecurityEvent


@dataclass(frozen=True)
class InferenceResult:
    score: float
    is_anomaly: bool
    model_version: str
    feature_schema_version: str


class MLRuntime:
    def __init__(self) -> None:
        self.model: Any | None = None
        self.model_version: str | None = None
        self.error: str | None = "model not loaded"

    def load(self, path: str) -> None:
        self.model = None
        self.model_version = None
        artifact = Path(path)
        checksum_path = artifact.with_suffix(artifact.suffix + ".sha256")
        if not artifact.is_file() or not checksum_path.is_file():
            self.error = "model artifact unavailable"
            return
        try:
            expected = checksum_path.read_text(encoding="ascii").strip()
            actual = hashlib.sha256(artifact.read_bytes()).hexdigest()
        except OSError:
            self.error = "model artifact unreadable"
            return
        if not expected or actual != expected:
            self.error = "model checksum mismatch"
            return
        try:
            bundle = joblib.load(artifact)
        except Exception:  # serialized artifacts can fail in library-specific ways
            self.error = "model artifact corrupt"
            return
        if (
            not isinstance(bundle, dict)
            or bundle.get("feature_schema_version") != FEATURE_SCHEMA_VERSION
            or tuple(bundle.get("feature_names", ())) != FEATURE_NAMES
            or not isinstance(bundle.get("model_version"), str)
            or not hasattr(bundle.get("model"), "decision_function")
        ):
            self.error = "model bundle is incompatible"
            return
        self.model = bundle["model"]
        self.model_version = bundle["model_version"]
        self.error = None

    @property
    def available(self) -> bool:
        return self.model is not None and self.error is None

    def predict(self, event: SecurityEvent) -> InferenceResult | None:
        if not self.available or self.model_version is None:
            return None
        model = self.model
        if model is None:
            return None
        decision = float(model.decision_function(extract_features(event))[0])
        score = float(np.clip(0.5 - decision * 4, 0, 1))
        return InferenceResult(score, score >= 0.7, self.model_version, FEATURE_SCHEMA_VERSION)


ml_runtime = MLRuntime()
