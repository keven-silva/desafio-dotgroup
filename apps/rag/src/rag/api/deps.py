from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status

from rag.adapters.embedding_factory import get_embedding_strategy
from rag.adapters.faiss_store import FaissVectorStore
from rag.core.config import Settings, get_settings
from rag.domain.ports import EmbeddingStrategy

AppSettings = Annotated[Settings, Depends(get_settings)]


@lru_cache
def _get_embedding_strategy() -> EmbeddingStrategy:
    # cacheado: instanciar de novo a cada request recarregaria o modelo (caro) do zero.
    return get_embedding_strategy(get_settings())


def get_embedding_strategy_dep() -> EmbeddingStrategy:
    return _get_embedding_strategy()


EmbeddingStrategyDep = Annotated[EmbeddingStrategy, Depends(get_embedding_strategy_dep)]


def get_store_for_ingest(settings: AppSettings, embedding_strategy: EmbeddingStrategyDep) -> FaissVectorStore:
    return FaissVectorStore(settings.rag_index_dir, embedding_strategy.dimension)


def get_store_for_search(settings: AppSettings, embedding_strategy: EmbeddingStrategyDep) -> FaissVectorStore:
    store = FaissVectorStore(settings.rag_index_dir, embedding_strategy.dimension)
    if not store.load():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Índice vazio — rode a ingestão primeiro (POST /ingest ou `rag ingest`)",
        )
    return store


StoreForIngestDep = Annotated[FaissVectorStore, Depends(get_store_for_ingest)]
StoreForSearchDep = Annotated[FaissVectorStore, Depends(get_store_for_search)]
