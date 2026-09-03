from typing import Protocol


class EmbeddingProvider(Protocol):
    dimensions: int

    def embed(self, text: str) -> list[float]: ...


class AnswerGenerator(Protocol):
    def generate(self, question: str, sources: list[tuple[str, str]]) -> str: ...
