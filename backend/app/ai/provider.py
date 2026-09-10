from app.ai.base import AIAnalyzer
from app.ai.fake import DeterministicFakeAnalyzer


def get_analyzer() -> AIAnalyzer:
    return DeterministicFakeAnalyzer()
