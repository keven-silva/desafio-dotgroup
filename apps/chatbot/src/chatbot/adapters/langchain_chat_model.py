from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from chatbot.domain.entities import Conversation, Message

SYSTEM_PROMPT = (
    "Você é um assistente especializado em desenvolvimento com Python. Responda de forma "
    "clara e objetiva, com exemplos de código quando fizer sentido. Se um contexto de "
    "referência for fornecido abaixo, use-o para embasar a resposta; caso contrário, responda "
    "com seu próprio conhecimento sobre Python."
)


class LangchainChatModel:
    """Implementa `ChatModel` com uma chain LCEL (`prompt | llm`) sobre `ChatOpenAI`."""

    def __init__(self, model: str, api_key: str) -> None:
        llm = ChatOpenAI(model=model, api_key=api_key)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "{system_prompt}"),
                MessagesPlaceholder("history"),
                ("human", "{input}"),
            ]
        )
        self._chain = prompt | llm

    def ask(self, conversation: Conversation, context: str | None) -> str:
        *history_messages, last_message = conversation.messages
        history = [self._to_langchain_message(m) for m in history_messages]
        system_prompt = SYSTEM_PROMPT if not context else f"{SYSTEM_PROMPT}\n\nContexto de referência:\n{context}"

        response = self._chain.invoke(
            {"system_prompt": system_prompt, "history": history, "input": last_message.content}
        )
        return response.content

    @staticmethod
    def _to_langchain_message(message: Message) -> BaseMessage:
        if message.role == "user":
            return HumanMessage(content=message.content)
        return AIMessage(content=message.content)
