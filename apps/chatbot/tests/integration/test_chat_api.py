from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from chatbot.api.deps import get_ask_question_service
from chatbot.main import app


class FakeAskQuestionService:
    def ask(self, session_id: str, message: str) -> str:
        return f"echo({session_id}): {message}"


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    app.dependency_overrides[get_ask_question_service] = lambda: FakeAskQuestionService()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_chat_returns_answer_from_service(client: AsyncClient) -> None:
    response = await client.post("/chat", json={"session_id": "s1", "message": "oi"})

    assert response.status_code == 200
    assert response.json() == {"session_id": "s1", "answer": "echo(s1): oi"}
