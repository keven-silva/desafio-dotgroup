import httpx

from chatbot.adapters.rag_http_client import RagHttpClient


class _FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=self)  # type: ignore[arg-type]

    def json(self) -> dict:
        return self._payload


def test_get_context_joins_results_from_rag_api(mocker) -> None:
    mocker.patch(
        "chatbot.adapters.rag_http_client.httpx.post",
        return_value=_FakeResponse({"results": [{"source": "async.md", "text": "trecho 1"}]}),
    )
    client = RagHttpClient(base_url="http://rag-service:8001")

    context = client.get_context("pergunta sobre python")

    assert context == "[async.md] trecho 1"


def test_get_context_returns_none_when_no_results(mocker) -> None:
    mocker.patch(
        "chatbot.adapters.rag_http_client.httpx.post", return_value=_FakeResponse({"results": []})
    )
    client = RagHttpClient(base_url="http://rag-service:8001")

    assert client.get_context("pergunta") is None


def test_get_context_returns_none_when_rag_service_is_unavailable(mocker) -> None:
    mocker.patch(
        "chatbot.adapters.rag_http_client.httpx.post", side_effect=httpx.ConnectError("connection refused")
    )
    client = RagHttpClient(base_url="http://rag-service:8001")

    assert client.get_context("pergunta") is None
