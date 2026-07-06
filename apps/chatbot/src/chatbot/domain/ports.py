from typing import Protocol

from chatbot.domain.entities import Conversation


class ChatModel(Protocol):
    """Integração com o LLM (LangChain por baixo) — o domínio só conhece este contrato."""

    def ask(self, conversation: Conversation, context: str | None) -> str: ...


class ConversationRepository(Protocol):
    def get(self, session_id: str) -> Conversation: ...
    def save(self, conversation: Conversation) -> None: ...


class RagContextProvider(Protocol):
    """Anti-corruption layer para o serviço `rag`: retorna `None` se indisponível (best-effort)."""

    def get_context(self, query: str, k: int = 3) -> str | None: ...
