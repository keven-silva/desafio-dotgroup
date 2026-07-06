from observability import get_logger

from chatbot.domain.ports import ChatModel, ConversationRepository, RagContextProvider

logger = get_logger()


class AskQuestionService:
    """Use case principal: recebe uma pergunta, busca contexto (best-effort) e responde."""

    def __init__(
        self,
        chat_model: ChatModel,
        conversation_repository: ConversationRepository,
        rag_context_provider: RagContextProvider,
        rag_context_k: int = 3,
    ) -> None:
        self._chat_model = chat_model
        self._conversations = conversation_repository
        self._rag = rag_context_provider
        self._rag_context_k = rag_context_k

    def ask(self, session_id: str, message: str) -> str:
        conversation = self._conversations.get(session_id)
        conversation.add_user_message(message)

        context = self._rag.get_context(message, k=self._rag_context_k)

        answer = self._chat_model.ask(conversation, context)
        conversation.add_assistant_message(answer)
        self._conversations.save(conversation)

        logger.info("chatbot.answered", session_id=session_id, used_rag_context=context is not None)
        return answer
