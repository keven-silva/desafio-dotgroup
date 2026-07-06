import numpy as np
from openai import OpenAI


class OpenAIEmbeddingStrategy:
    """Implementa `EmbeddingStrategy` via API da OpenAI (pago, precisa de rede/API key)."""

    def __init__(self, model_name: str = "text-embedding-3-small", api_key: str | None = None) -> None:
        self._model_name = model_name
        self._client = OpenAI(api_key=api_key)
        self._dimension: int | None = None

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(model=self._model_name, input=texts)
        vectors = [item.embedding for item in response.data]
        normalized = [self._normalize(vector) for vector in vectors]
        self._dimension = len(normalized[0]) if normalized else self._dimension
        return normalized

    @staticmethod
    def _normalize(vector: list[float]) -> list[float]:
        array = np.asarray(vector, dtype=float)
        norm = np.linalg.norm(array)
        if norm == 0:
            return vector
        return (array / norm).tolist()

    @property
    def dimension(self) -> int:
        if self._dimension is None:
            self._dimension = len(self.embed(["dimension probe"])[0])
        return self._dimension
