import pytest

from rag.adapters.embedding_factory import get_embedding_strategy
from rag.adapters.openai_strategy import OpenAIEmbeddingStrategy
from rag.core.config import Settings


def test_factory_returns_sentence_transformers_strategy(mocker) -> None:
    fake_strategy = object()
    mock_cls = mocker.patch(
        "rag.adapters.sentence_transformers_strategy.SentenceTransformersEmbeddingStrategy",
        return_value=fake_strategy,
    )
    settings = Settings(embedding_provider="sentence-transformers", embedding_model="all-MiniLM-L6-v2")

    strategy = get_embedding_strategy(settings)

    mock_cls.assert_called_once_with("all-MiniLM-L6-v2")
    assert strategy is fake_strategy


def test_factory_returns_openai_strategy() -> None:
    settings = Settings(
        embedding_provider="openai", embedding_model="text-embedding-3-small", openai_api_key="test-key"
    )

    strategy = get_embedding_strategy(settings)

    assert isinstance(strategy, OpenAIEmbeddingStrategy)


def test_factory_raises_for_unknown_provider() -> None:
    settings = Settings(embedding_provider="unknown-provider")

    with pytest.raises(ValueError, match="unknown-provider"):
        get_embedding_strategy(settings)
