from sentence_transformers import SentenceTransformer


class SentenceTransformersEmbeddingStrategy:
    """Implementa `EmbeddingStrategy` com um modelo local (sem custo, sem rede)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).tolist()

    @property
    def dimension(self) -> int:
        return self._model.get_embedding_dimension()
