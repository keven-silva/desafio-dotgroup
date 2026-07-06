from observability import configure_logging

from chatbot.adapters.in_memory_conversation_repository import InMemoryConversationRepository
from chatbot.adapters.langchain_chat_model import LangchainChatModel
from chatbot.adapters.rag_http_client import RagHttpClient
from chatbot.core.config import get_settings
from chatbot.service_layer.services import AskQuestionService

SESSION_ID = "cli-session"


def main() -> None:
    settings = get_settings()
    configure_logging("chatbot", level=settings.log_level, json=settings.log_json)

    service = AskQuestionService(
        chat_model=LangchainChatModel(model=settings.chatbot_model, api_key=settings.openai_api_key),
        conversation_repository=InMemoryConversationRepository(),
        rag_context_provider=RagHttpClient(base_url=settings.rag_api_url),
        rag_context_k=settings.rag_context_k,
    )

    print("Chatbot de desenvolvimento Python — digite 'sair' para encerrar.\n")
    while True:
        try:
            message = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if message.lower() in {"sair", "exit", "quit"}:
            break
        if not message:
            continue

        answer = service.ask(SESSION_ID, message)
        print(f"\n{answer}\n")


if __name__ == "__main__":
    main()
