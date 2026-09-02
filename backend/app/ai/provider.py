from app.ai.base import AIAnalyzer
from app.ai.fake import DeterministicFakeAnalyzer


def get_analyzer() -> AIAnalyzer:
    """Return the configured analyzer without coupling providers to HTTP routes."""
    return DeterministicFakeAnalyzer()
