from pathlib import Path

from observability import get_logger

from rag.adapters.chunker import chunk_documents
from rag.adapters.loader import load_documents
from rag.domain.entities import SearchResult
from rag.domain.ports import EmbeddingStrategy, VectorStore

logger = get_logger()


def ingest_documents(
    *,
    data_dir: Path,
    embedding_strategy: EmbeddingStrategy,
    store: VectorStore,
    chunk_size: int,
    chunk_overlap: int,
) -> int:
    """Use case: lê os documentos de `data_dir`, gera embeddings e indexa no `store`.

    Reconstrói o índice do zero a cada chamada (uma ingestão em lote, não incremental).
    """
    documents = load_documents(data_dir)
    logger.info("rag.ingest.documents_loaded", count=len(documents))

    chunks = chunk_documents(documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    logger.info("rag.ingest.chunks_created", count=len(chunks))

    if chunks:
        vectors = embedding_strategy.embed([chunk.text for chunk in chunks])
        store.add(chunks, vectors)

    store.save()
    logger.info("rag.ingest.completed", chunks=len(chunks))
    return len(chunks)


def semantic_search(
    query: str, k: int, *, embedding_strategy: EmbeddingStrategy, store: VectorStore
) -> list[SearchResult]:
    """Use case: embeda a query e busca os `k` chunks mais similares no `store`."""
    query_vector = embedding_strategy.embed([query])[0]
    results = store.search(query_vector, k)
    logger.info("rag.search.completed", query=query, results=len(results))
    return results
