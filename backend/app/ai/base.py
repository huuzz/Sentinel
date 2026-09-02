from typing import Protocol

from app.schemas.analysis import AnalysisContext, AnalysisResult


class AIAnalyzer(Protocol):
    provider: str
    model: str

    async def analyze(self, context: AnalysisContext) -> AnalysisResult: ...
