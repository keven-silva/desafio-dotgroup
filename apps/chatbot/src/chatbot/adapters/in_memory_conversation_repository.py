from chatbot.domain.entities import Conversation


class InMemoryConversationRepository:
    """Implementa `ConversationRepository` com um dict em processo (por `session_id`).

    Suficiente para o escopo do desafio; trocar por Redis/DB no futuro não afeta o
    `service_layer`, que só conhece o port.
    """

    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}

    def get(self, session_id: str) -> Conversation:
        return self._conversations.get(session_id, Conversation(session_id=session_id))

    def save(self, conversation: Conversation) -> None:
        self._conversations[conversation.session_id] = conversation
