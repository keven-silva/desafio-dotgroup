import httpx
from observability import get_logger

logger = get_logger()


class RagHttpClient:
    """Implementa `RagContextProvider` chamando a API HTTP do serviço `rag` (POST /search).

    Best-effort: qualquer falha de rede/serviço indisponível retorna `None` em vez de
    propagar a exceção — o chatbot continua respondendo sem contexto recuperado.
    """

    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        # 15s cobre o cold-start do serviço `rag` (primeira chamada carrega o modelo de
        # embedding); chamadas subsequentes respondem em dezenas de milissegundos.
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def get_context(self, query: str, k: int = 3) -> str | None:
        try:
            response = httpx.post(
                f"{self._base_url}/search", json={"query": query, "k": k}, timeout=self._timeout
            )
            response.raise_for_status()
        except httpx.HTTPError:
            logger.warning("rag_context.unavailable", rag_api_url=self._base_url)
            return None

        results = response.json().get("results", [])
        if not results:
            return None

        return "\n\n".join(f"[{item['source']}] {item['text']}" for item in results)
