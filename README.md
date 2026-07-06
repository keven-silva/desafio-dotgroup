# desafio-dotgroup

Três serviços independentes, organizados em DDD (bounded contexts), num monorepo gerenciado
com `uv workspace`:

| Serviço | O que faz | Stack |
|---|---|---|
| [`library_api`](apps/library_api) | API REST de biblioteca (autores, livros, membros, empréstimos) | FastAPI + SQLAlchemy (async) + PostgreSQL + Alembic |
| [`rag`](apps/rag) | Ingestão de artigos/posts, geração de embeddings e busca semântica | FastAPI + `sentence-transformers`/OpenAI + FAISS |
| [`chatbot`](apps/chatbot) | Chatbot de IA sobre desenvolvimento Python, com contexto do `rag` (RAG) | FastAPI + LangChain (LCEL) + OpenAI |

Cada serviço é isolado de verdade: tem seu próprio `pyproject.toml`, suas próprias
configurações (`.env`), e não importa código de negócio de outro serviço — a única
comunicação entre eles é via HTTP (o `chatbot` chama a API do `rag`). A única dependência
compartilhada é [`libs/observability`](libs/observability), que é infraestrutura transversal
(logging estruturado), não lógica de domínio.

## Arquitetura

Cada serviço segue o mesmo esqueleto em camadas (inspirado em DDD/hexagonal —
"Architecture Patterns with Python"):

```
domain/         # entidades ricas (regras de negócio) + ports (Protocol) que o domínio precisa
service_layer/  # use cases: orquestram entidades + ports, não conhecem FastAPI nem infra concreta
adapters/       # implementações concretas dos ports (SQLAlchemy, FAISS, LangChain, HTTP client)
api/            # FastAPI routers + schemas Pydantic + wiring (deps.py)
```

A `library_api` tem dois subdomínios (bounded contexts) claros dentro do mesmo serviço:
`catalog` (autores/livros) e `lending` (membros/empréstimos) — veja
[apps/library_api/src/library_api](apps/library_api/src/library_api).

## Pré-requisitos

- [`uv`](https://docs.astral.sh/uv/) (gerencia o workspace Python)
- Docker + Docker Compose (Postgres da `library_api`)
- Uma OpenAI API key (só necessária para o `chatbot` responder de verdade)

## Setup

```bash
cp .env.example .env   # ajuste OPENAI_API_KEY e o resto se necessário
uv sync --all-packages  # instala as dependências de todos os serviços num único .venv

docker compose up -d postgres
uv run --package library-api alembic upgrade head
```

## Rodando cada serviço

```bash
# API de biblioteca — http://localhost:8000/docs
uv run --package library-api uvicorn library_api.main:app --reload --port 8000

# Serviço de embeddings/busca semântica — http://localhost:8001/docs
uv run --package rag rag ingest                      # popula o índice FAISS a partir de apps/rag/data/raw
uv run --package rag uvicorn rag.main:app --reload --port 8001

# Chatbot — http://localhost:8002/docs (precisa do `rag` rodando para ter contexto RAG)
RAG_API_URL=http://localhost:8001 uv run --package chatbot uvicorn chatbot.main:app --reload --port 8002
```

Também é possível interagir com a busca semântica e com o chatbot direto pelo terminal:

```bash
uv run --package rag rag search "como funciona async/await em python?" --k 3
uv run --package chatbot chatbot
```

## Variáveis de ambiente

Veja `.env.example` na raiz para a lista completa. Principais:

| Variável | Serviço | Descrição |
|---|---|---|
| `DATABASE_URL` | `library_api` | conexão Postgres (async, driver `asyncpg`) |
| `EMBEDDING_PROVIDER` | `rag` | `sentence-transformers` (local, padrão) ou `openai` |
| `EMBEDDING_MODEL` | `rag` | modelo usado pela estratégia ativa (Strategy Pattern) |
| `RAG_API_URL` | `chatbot` | URL onde o serviço `rag` está rodando |
| `OPENAI_API_KEY` | `chatbot` (e `rag` se `EMBEDDING_PROVIDER=openai`) | chave da API da OpenAI |
| `LOG_LEVEL` / `LOG_JSON` | todos | nível de log e se a saída é JSON estruturado |

## Logs estruturados

Todos os serviços usam `libs/observability` para logar em JSON (via `structlog`), com um
`request_id` por requisição (propagado pelo header `X-Request-ID`), latência e eventos de
domínio relevantes (ex: `loan.created`, `rag.search.completed`, `chatbot.answered`):

```json
{"event": "request.finished", "request_id": "...", "status_code": 200, "duration_ms": 12.4, "service": "library_api"}
```

## Testes

```bash
# rodados a partir da raiz do repo — o caminho no final garante que o pytest use
# o pyproject.toml (e config de asyncio) daquele app, não o da raiz do workspace
uv run --package library-api pytest apps/library_api
uv run --package rag pytest apps/rag
uv run --package chatbot pytest apps/chatbot
uv run --package observability pytest libs/observability
```

Testes unitários não tocam rede/infra externa (mockam OpenAI, chamadas HTTP entre serviços
etc.); testes de integração sobem o app FastAPI real (com `httpx.AsyncClient`) e, na
`library_api`, usam um banco SQLite em memória. `library_api/tests/test_migrations.py` roda
`alembic upgrade head` contra o Postgres real do `docker-compose` (pulado automaticamente se
o Postgres não estiver acessível).

## Documentação do pipeline de embeddings

Veja [docs/embeddings.md](docs/embeddings.md): explica o pipeline completo (ingestão → chunking
→ embedding → indexação FAISS → busca) e mostra exemplos reais de consultas com resultados.
