import math

import numpy as np

from app.models.security_event import SecurityEvent

FEATURE_SCHEMA_VERSION = "1.0"
FEATURE_NAMES = (
    "hour_sin",
    "hour_cos",
    "is_failure",
    "is_server_error",
    "has_user",
    "endpoint_length",
)


def extract_features(event: SecurityEvent) -> np.ndarray:
    hour = event.timestamp.hour + event.timestamp.minute / 60
    angle = 2 * math.pi * hour / 24
    return np.asarray(
        [
            [
                math.sin(angle),
                math.cos(angle),
                float(event.outcome == "failure"),
                float(event.status_code is not None and event.status_code >= 500),
                float(bool(event.user_identifier)),
                min(len(event.endpoint or ""), 500) / 500,
            ]
        ],
        dtype=np.float64,
    )
