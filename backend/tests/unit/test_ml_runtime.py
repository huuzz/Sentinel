import hashlib
import pickle
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from app.ml.features import FEATURE_NAMES, FEATURE_SCHEMA_VERSION, extract_features
from app.ml.runtime import MLRuntime
from app.models.security_event import SecurityEvent


class FakeModel:
    def decision_function(self, _: np.ndarray) -> np.ndarray:
        return np.asarray([-0.1])


def write_bundle(path: Path, schema: str = FEATURE_SCHEMA_VERSION) -> None:
    with path.open("wb") as handle:
        pickle.dump(
            {
                "model": FakeModel(),
                "model_version": "test-v1",
                "feature_schema_version": schema,
                "feature_names": FEATURE_NAMES,
            },
            handle,
        )
    path.with_suffix(path.suffix + ".sha256").write_text(
        hashlib.sha256(path.read_bytes()).hexdigest(), encoding="ascii"
    )


def test_missing_and_incompatible_models_fail_closed(tmp_path: Path) -> None:
    runtime = MLRuntime()
    runtime.load(str(tmp_path / "missing.joblib"))
    assert not runtime.available
    path = tmp_path / "model.joblib"
    write_bundle(path, "wrong-schema")
    runtime.load(str(path))
    assert not runtime.available
    assert runtime.error == "model bundle is incompatible"
    corrupt = tmp_path / "corrupt.joblib"
    corrupt.write_bytes(b"not a serialized model")
    corrupt.with_suffix(corrupt.suffix + ".sha256").write_text(
        hashlib.sha256(corrupt.read_bytes()).hexdigest(), encoding="ascii"
    )
    runtime.load(str(corrupt))
    assert not runtime.available
    assert runtime.error == "model artifact corrupt"


def test_compatible_model_scores_deterministically(tmp_path: Path) -> None:
    path = tmp_path / "model.joblib"
    write_bundle(path)
    runtime = MLRuntime()
    runtime.load(str(path))
    event = SecurityEvent(
        timestamp=datetime(2026, 9, 2, 2, tzinfo=UTC),
        event_type="api_request",
        source="test",
        outcome="failure",
        source_ip="192.0.2.1",
        endpoint="/example",
        event_metadata={},
        simulated=True,
    )
    assert extract_features(event).shape == (1, len(FEATURE_NAMES))
    first = runtime.predict(event)
    second = runtime.predict(event)
    assert first == second
    assert first is not None and first.is_anomaly and first.score == 0.9
