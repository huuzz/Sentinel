import hashlib
import math
import re


class DeterministicEmbeddingProvider:
    dimensions = 64

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in re.findall(r"[a-z0-9]+", text.lower())[:2000]:
            digest = hashlib.sha256(token.encode()).digest()
            index = int.from_bytes(digest[:2], "big") % self.dimensions
            vector[index] += 1.0 if digest[2] % 2 else -1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class DeterministicAnswerGenerator:
    def generate(self, question: str, sources: list[tuple[str, str]]) -> str:
        del question  # questions and retrieved content are data, never executable instructions
        if not sources:
            return "No grounded answer is available from the current knowledge base."
        titles = ", ".join(title for title, _ in sources)
        return (
            f"Relevant security guidance was retrieved from: {titles}. "
            "Review the cited excerpts below and apply them using your approved "
            "incident-response process."
        )
