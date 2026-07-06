from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from chatbot.api.deps import AskQuestionServiceDep
from chatbot.api.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(data: ChatRequest, service: AskQuestionServiceDep) -> ChatResponse:
    # chat_model.ask()/rag_http_client são síncronos (chamadas de rede bloqueantes) —
    # rodam em threadpool para não travar o event loop.
    answer = await run_in_threadpool(service.ask, data.session_id, data.message)
    return ChatResponse(session_id=data.session_id, answer=answer)
