from unittest.mock import MagicMock

from chatbot.adapters.langchain_chat_model import LangchainChatModel
from chatbot.domain.entities import Conversation


def _model_with_fake_chain(answer: str) -> tuple[LangchainChatModel, MagicMock]:
    model = LangchainChatModel(model="gpt-4o-mini", api_key="test-key")
    fake_response = MagicMock(content=answer)
    # substitui a chain por um dublê simples — evitar `mocker.patch.object` aqui porque
    # `_chain` é um `RunnableSequence` (Pydantic) cujo `__delattr__` quebra no teardown do patch.
    model._chain = MagicMock(invoke=MagicMock(return_value=fake_response))
    return model, model._chain


def test_ask_builds_prompt_with_history_context_and_returns_llm_answer() -> None:
    model, fake_chain = _model_with_fake_chain("resposta do llm")

    conversation = Conversation(session_id="s1")
    conversation.add_user_message("primeira pergunta")
    conversation.add_assistant_message("primeira resposta")
    conversation.add_user_message("segunda pergunta")

    answer = model.ask(conversation, context="[doc.md] trecho relevante")

    assert answer == "resposta do llm"

    call_kwargs = fake_chain.invoke.call_args.args[0]
    assert call_kwargs["input"] == "segunda pergunta"
    assert "trecho relevante" in call_kwargs["system_prompt"]
    assert len(call_kwargs["history"]) == 2


def test_ask_without_context_uses_base_system_prompt() -> None:
    model, fake_chain = _model_with_fake_chain("resposta")

    conversation = Conversation(session_id="s1")
    conversation.add_user_message("pergunta única")

    model.ask(conversation, context=None)

    call_kwargs = fake_chain.invoke.call_args.args[0]
    assert "Contexto de referência" not in call_kwargs["system_prompt"]
    assert call_kwargs["history"] == []
