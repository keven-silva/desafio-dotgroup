import argparse
import sys

from observability import configure_logging

from rag.adapters.embedding_factory import get_embedding_strategy
from rag.adapters.faiss_store import FaissVectorStore
from rag.core.config import Settings, get_settings
from rag.domain.ports import EmbeddingStrategy
from rag.service_layer.services import ingest_documents, semantic_search


def _build_store(settings: Settings, embedding_strategy: EmbeddingStrategy, *, for_search: bool) -> FaissVectorStore:
    store = FaissVectorStore(settings.rag_index_dir, embedding_strategy.dimension)
    if for_search and not store.load():
        print("Índice vazio — rode `rag ingest` primeiro.", file=sys.stderr)
        raise SystemExit(1)
    return store


def cmd_ingest(args: argparse.Namespace) -> None:
    settings = get_settings()
    embedding_strategy = get_embedding_strategy(settings)
    store = _build_store(settings, embedding_strategy, for_search=False)

    chunks_indexed = ingest_documents(
        data_dir=settings.rag_data_dir,
        embedding_strategy=embedding_strategy,
        store=store,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    print(f"{chunks_indexed} chunks indexados em {settings.rag_index_dir}")


def cmd_search(args: argparse.Namespace) -> None:
    settings = get_settings()
    embedding_strategy = get_embedding_strategy(settings)
    store = _build_store(settings, embedding_strategy, for_search=True)

    results = semantic_search(args.query, args.k, embedding_strategy=embedding_strategy, store=store)
    if not results:
        print("Nenhum resultado encontrado.")
        return

    for position, result in enumerate(results, start=1):
        print(f"[{position}] score={result.score:.4f} source={result.source}")
        print(f"    {result.text[:200]}...")


def main() -> None:
    settings = get_settings()
    configure_logging("rag", level=settings.log_level, json=settings.log_json)

    parser = argparse.ArgumentParser(prog="rag")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Roda o pipeline de ingestão completo")
    ingest_parser.set_defaults(func=cmd_ingest)

    search_parser = subparsers.add_parser("search", help="Busca semântica no índice")
    search_parser.add_argument("query", type=str)
    search_parser.add_argument("--k", type=int, default=3)
    search_parser.set_defaults(func=cmd_search)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
