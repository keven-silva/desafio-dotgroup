# chatbot

Chatbot de IA generativa especializado em desenvolvimento Python, usando LangChain + OpenAI, com contexto opcional recuperado do pacote `rag` (RAG).

## Uso

```bash
uv run --package chatbot chatbot                 # modo interativo no terminal
uv run --package chatbot uvicorn chatbot.main:app --reload   # API HTTP
```

## Testes

```bash
uv run --package chatbot pytest
```
