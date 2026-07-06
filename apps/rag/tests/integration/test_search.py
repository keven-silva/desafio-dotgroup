from pathlib import Path

from rag.adapters.faiss_store import FaissVectorStore
from rag.adapters.sentence_transformers_strategy import SentenceTransformersEmbeddingStrategy
from rag.service_layer.services import ingest_documents, semantic_search


def test_ingest_then_search_returns_the_semantically_relevant_document(tmp_path: Path) -> None:
    data_dir = tmp_path / "raw"
    index_dir = tmp_path / "index"
    data_dir.mkdir()

    (data_dir / "python-async.md").write_text(
        "Python usa async e await para programação assíncrona com asyncio, permitindo "
        "que operações de rede e I/O não bloqueiem o event loop.",
        encoding="utf-8",
    )
    (data_dir / "receita-de-bolo.md").write_text(
        "Para fazer um bolo de chocolate, misture farinha, açúcar, ovos e chocolate em pó, "
        "depois leve ao forno preaquecido por quarenta minutos.",
        encoding="utf-8",
    )

    embedding_strategy = SentenceTransformersEmbeddingStrategy("paraphrase-multilingual-MiniLM-L12-v2")
    ingest_store = FaissVectorStore(index_dir, embedding_strategy.dimension)

    chunks_indexed = ingest_documents(
        data_dir=data_dir,
        embedding_strategy=embedding_strategy,
        store=ingest_store,
        chunk_size=200,
        chunk_overlap=20,
    )
    assert chunks_indexed >= 2

    search_store = FaissVectorStore(index_dir, embedding_strategy.dimension)
    assert search_store.load() is True

    results = semantic_search(
        "como funciona programação assíncrona em python?",
        k=1,
        embedding_strategy=embedding_strategy,
        store=search_store,
    )

    assert len(results) == 1
    assert results[0].source == "python-async.md"
