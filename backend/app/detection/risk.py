from app.models.alert import AlertSeverity

SEVERITY_BASE = {
    AlertSeverity.LOW: 20.0,
    AlertSeverity.MEDIUM: 45.0,
    AlertSeverity.HIGH: 70.0,
    AlertSeverity.CRITICAL: 85.0,
}


def calculate_risk(severity: AlertSeverity, confidence: float, evidence_count: int) -> float:
    """Score = severity base + up to 10 confidence points + up to 10 evidence points."""
    bounded_confidence = min(1.0, max(0.0, confidence))
    evidence_bonus = min(10.0, max(0, evidence_count) * 1.0)
    return round(min(100.0, SEVERITY_BASE[severity] + bounded_confidence * 10 + evidence_bonus), 1)
