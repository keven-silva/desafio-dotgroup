from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from rag.api.deps import AppSettings, EmbeddingStrategyDep, StoreForIngestDep, StoreForSearchDep
from rag.api.schemas import IngestResponse, SearchRequest, SearchResponse, SearchResultSchema
from rag.service_layer.services import ingest_documents, semantic_search

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    settings: AppSettings, embedding_strategy: EmbeddingStrategyDep, store: StoreForIngestDep
) -> IngestResponse:
    # embedding/indexação são síncronos e podem ser custosos — não bloqueiam o event loop.
    chunks_indexed = await run_in_threadpool(
        ingest_documents,
        data_dir=settings.rag_data_dir,
        embedding_strategy=embedding_strategy,
        store=store,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return IngestResponse(chunks_indexed=chunks_indexed)


@router.post("/search", response_model=SearchResponse)
async def search(
    data: SearchRequest, embedding_strategy: EmbeddingStrategyDep, store: StoreForSearchDep
) -> SearchResponse:
    results = await run_in_threadpool(
        semantic_search, data.query, data.k, embedding_strategy=embedding_strategy, store=store
    )
    return SearchResponse(
        results=[SearchResultSchema(text=r.text, source=r.source, score=r.score) for r in results]
    )
