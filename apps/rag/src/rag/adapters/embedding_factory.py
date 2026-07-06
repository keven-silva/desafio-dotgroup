from rag.core.config import Settings
from rag.domain.ports import EmbeddingStrategy


def get_embedding_strategy(settings: Settings) -> EmbeddingStrategy:
    """Factory do Strategy Pattern: escolhe a implementação por config, sem o resto do
    pipeline (`service_layer`, `faiss_store`) precisar saber qual está ativa."""
    if settings.embedding_provider == "sentence-transformers":
        from rag.adapters.sentence_transformers_strategy import SentenceTransformersEmbeddingStrategy

        return SentenceTransformersEmbeddingStrategy(settings.embedding_model)

    if settings.embedding_provider == "openai":
        from rag.adapters.openai_strategy import OpenAIEmbeddingStrategy

        return OpenAIEmbeddingStrategy(settings.embedding_model, api_key=settings.openai_api_key)

    raise ValueError(f"Provedor de embedding desconhecido: {settings.embedding_provider}")
