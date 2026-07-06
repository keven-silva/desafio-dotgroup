from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from rag.api.deps import get_embedding_strategy_dep, get_store_for_ingest, get_store_for_search
from rag.domain.entities import Chunk, SearchResult
from rag.main import app


class FakeEmbeddingStrategy:
    dimension = 3

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class FakeStore:
    def __init__(self) -> None:
        self.saved = False

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        self.received_chunks = chunks

    def search(self, query_vector: list[float], k: int) -> list[SearchResult]:
        return [SearchResult(text="Python usa async/await", source="async.md", score=0.99)][:k]

    def save(self) -> None:
        self.saved = True

    def load(self) -> bool:
        return True


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    app.dependency_overrides[get_embedding_strategy_dep] = lambda: FakeEmbeddingStrategy()
    app.dependency_overrides[get_store_for_ingest] = lambda: FakeStore()
    app.dependency_overrides[get_store_for_search] = lambda: FakeStore()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_search_returns_results_from_store(client: AsyncClient) -> None:
    response = await client.post("/search", json={"query": "async em python", "k": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["results"] == [{"text": "Python usa async/await", "source": "async.md", "score": 0.99}]
