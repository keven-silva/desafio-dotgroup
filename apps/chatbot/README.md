# chatbot

Chatbot de IA generativa especializado em desenvolvimento Python, usando LangChain (LCEL) +
OpenAI, com contexto opcional recuperado do serviço `rag` via HTTP (RAG best-effort — se o
`rag` estiver indisponível, o chatbot responde sem contexto).

Projeto `uv` independente — tem seu próprio `pyproject.toml`/`uv.lock`/`.venv`, sem depender de
workspace com os outros serviços. A única dependência local é `../../libs/observability`
(logging estruturado compartilhado); a integração com `rag` é via HTTP (`RAG_API_URL`), não
import Python.

## Setup

```bash
cd apps/chatbot
uv sync
cp .env.example .env   # defina OPENAI_API_KEY de verdade e ajuste RAG_API_URL se necessário
```

## Uso — CLI

```bash
uv run chatbot   # modo interativo no terminal
```

## Uso — API HTTP

Precisa do serviço `rag` rodando (em outro terminal) para ter contexto RAG; sem ele, o chatbot
ainda responde, só que sem contexto recuperado.

```bash
uv run uvicorn chatbot.main:app --reload --port 8002
```

Docs interativas em `http://localhost:8002/api/docs`. Endpoint: `POST /chat`.

## Testes

```bash
uv run pytest
```
