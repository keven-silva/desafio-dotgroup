from chatbot.adapters.in_memory_conversation_repository import InMemoryConversationRepository
from chatbot.domain.entities import Conversation
from chatbot.service_layer.services import AskQuestionService


class FakeChatModel:
    def __init__(self, answer: str = "resposta fake") -> None:
        self.answer = answer
        self.last_seen_contents: list[str] | None = None
        self.last_context: str | None = None

    def ask(self, conversation: Conversation, context: str | None) -> str:
        # snapshot: `conversation` é mutada pelo service logo após este retorno
        # (a resposta do assistente é anexada), então guardamos uma cópia agora.
        self.last_seen_contents = [m.content for m in conversation.messages]
        self.last_context = context
        return self.answer


class FakeRagContextProvider:
    def __init__(self, context: str | None) -> None:
        self._context = context

    def get_context(self, query: str, k: int = 3) -> str | None:
        return self._context


def _make_service(chat_model: FakeChatModel, context: str | None) -> AskQuestionService:
    return AskQuestionService(
        chat_model=chat_model,
        conversation_repository=InMemoryConversationRepository(),
        rag_context_provider=FakeRagContextProvider(context),
    )


def test_ask_returns_the_chat_model_answer() -> None:
    chat_model = FakeChatModel(answer="use asyncio.gather para concorrência")
    service = _make_service(chat_model, context=None)

    answer = service.ask("session-1", "como rodar tarefas concorrentes em python?")

    assert answer == "use asyncio.gather para concorrência"


def test_ask_passes_rag_context_to_chat_model() -> None:
    chat_model = FakeChatModel()
    service = _make_service(chat_model, context="[async.md] trecho relevante")

    service.ask("session-1", "pergunta")

    assert chat_model.last_context == "[async.md] trecho relevante"


def test_ask_keeps_conversation_history_across_calls() -> None:
    chat_model = FakeChatModel()
    service = _make_service(chat_model, context=None)

    service.ask("session-1", "primeira pergunta")
    service.ask("session-1", "segunda pergunta")

    assert chat_model.last_seen_contents == ["primeira pergunta", "resposta fake", "segunda pergunta"]


def test_ask_uses_separate_history_per_session() -> None:
    chat_model = FakeChatModel()
    service = _make_service(chat_model, context=None)

    service.ask("session-a", "pergunta da sessão A")
    service.ask("session-b", "pergunta da sessão B")

    assert chat_model.last_seen_contents == ["pergunta da sessão B"]
