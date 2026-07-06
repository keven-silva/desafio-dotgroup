class PythonDevChatbot:
    """Chatbot focado em desenvolvimento Python."""

    _knowledge_base = {
        "fastapi": "Use routers por domínio, dependências com DI e validação com Pydantic.",
        "sqlalchemy": "Prefira SQLAlchemy 2.0 com tipagem Mapped e sessões curtas por request.",
        "teste": "Crie testes pequenos e focados nos contratos de entrada e saída.",
        "solid": "Aplique SRP para separar regras de negócio em services e mantenha baixo acoplamento.",
        "dry": "Extraia comportamentos repetidos para services/utilitários reutilizáveis.",
    }

    def answer(self, question: str) -> str:
        lowered = question.lower()
        for keyword, response in self._knowledge_base.items():
            if keyword in lowered:
                return response
        return (
            "Foque em boas práticas Python: tipagem, testes, separação por camadas "
            "e tratamento explícito de erros."
        )
