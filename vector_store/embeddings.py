import hashlib


class EmbeddingGenerator:
    def __init__(self, dimensions: int = 16) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = [digest[i] / 255 for i in range(self.dimensions)]
        return values
