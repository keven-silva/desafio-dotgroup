from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from chatbot.adapters.in_memory_conversation_repository import InMemoryConversationRepository
from chatbot.adapters.langchain_chat_model import LangchainChatModel
from chatbot.adapters.rag_http_client import RagHttpClient
from chatbot.core.config import Settings, get_settings
from chatbot.service_layer.services import AskQuestionService

AppSettings = Annotated[Settings, Depends(get_settings)]


@lru_cache
def _get_conversation_repository() -> InMemoryConversationRepository:
    # cacheado: precisa ser o mesmo dict entre requests para manter histórico por sessão.
    return InMemoryConversationRepository()


@lru_cache
def _get_chat_model() -> LangchainChatModel:
    settings = get_settings()
    return LangchainChatModel(model=settings.chatbot_model, api_key=settings.openai_api_key)


@lru_cache
def _get_rag_context_provider() -> RagHttpClient:
    settings = get_settings()
    return RagHttpClient(base_url=settings.rag_api_url)


def get_ask_question_service(settings: AppSettings) -> AskQuestionService:
    return AskQuestionService(
        chat_model=_get_chat_model(),
        conversation_repository=_get_conversation_repository(),
        rag_context_provider=_get_rag_context_provider(),
        rag_context_k=settings.rag_context_k,
    )


AskQuestionServiceDep = Annotated[AskQuestionService, Depends(get_ask_question_service)]
