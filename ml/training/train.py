"""Train SentinelAI's educational Isolation Forest on reproducible synthetic data."""
import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from app.ml.features import FEATURE_NAMES, FEATURE_SCHEMA_VERSION  # noqa: E402

MODEL_VERSION = "isolation-forest-synthetic-v1"


def generate(seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    normal_hours = rng.uniform(7, 20, 1900)
    normal = np.column_stack(
        [
            np.sin(2 * np.pi * normal_hours / 24),
            np.cos(2 * np.pi * normal_hours / 24),
            rng.binomial(1, 0.04, 1900),
            rng.binomial(1, 0.01, 1900),
            rng.binomial(1, 0.65, 1900),
            np.clip(rng.normal(0.12, 0.05, 1900), 0, 1),
        ]
    )
    anomaly_hours = rng.uniform(0, 5, 100)
    anomalies = np.column_stack(
        [
            np.sin(2 * np.pi * anomaly_hours / 24),
            np.cos(2 * np.pi * anomaly_hours / 24),
            rng.binomial(1, 0.8, 100),
            rng.binomial(1, 0.5, 100),
            rng.binomial(1, 0.3, 100),
            rng.uniform(0.7, 1, 100),
        ]
    )
    return np.vstack([normal, anomalies]), np.asarray([0] * 1900 + [1] * 100)


def main() -> None:
    features, labels = generate()
    dataset_path = ROOT / "ml" / "datasets" / "synthetic_events_v1.csv"
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    with dataset_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([*FEATURE_NAMES, "synthetic_label"])
        writer.writerows(np.column_stack([features, labels]))
    model = IsolationForest(n_estimators=150, contamination=0.05, random_state=42, n_jobs=1)
    model.fit(features)
    bundle = {
        "model": model,
        "model_version": MODEL_VERSION,
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "feature_names": FEATURE_NAMES,
        "training": {"seed": 42, "rows": len(features), "synthetic_anomalies": int(labels.sum())},
    }
    model_path = ROOT / "ml" / "models" / "isolation_forest_v1.joblib"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, model_path)
    checksum = hashlib.sha256(model_path.read_bytes()).hexdigest()
    model_path.with_suffix(model_path.suffix + ".sha256").write_text(checksum, encoding="ascii")
    metadata = {**bundle["training"], "model_version": MODEL_VERSION, "feature_schema_version": FEATURE_SCHEMA_VERSION, "feature_names": FEATURE_NAMES, "limitations": "Synthetic educational data is not representative of production traffic."}
    (model_path.parent / "isolation_forest_v1.metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    runtime_dir = ROOT / "backend" / "app" / "ml" / "artifacts"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    for source in (model_path, model_path.with_suffix(model_path.suffix + ".sha256")):
        shutil.copy2(source, runtime_dir / source.name)
    print(f"trained {MODEL_VERSION}: {len(features)} rows, sha256={checksum}")


if __name__ == "__main__":
    main()
