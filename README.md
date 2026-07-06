# desafio-dotgroup

Três serviços **totalmente independentes** (cada um com seu próprio `pyproject.toml`,
`uv.lock` e `.venv`), organizados internamente em DDD (bounded contexts):

| Serviço | O que faz | Stack | Porta sugerida |
|---|---|---|---|
| [`library_api`](apps/library_api) | API REST de biblioteca (autores, livros, membros, empréstimos) | FastAPI + SQLAlchemy (async) + PostgreSQL + Alembic | 8000 |
| [`rag`](apps/rag) | Ingestão de artigos/posts, geração de embeddings e busca semântica | FastAPI + `sentence-transformers`/OpenAI + FAISS | 8001 |
| [`chatbot`](apps/chatbot) | Chatbot de IA sobre desenvolvimento Python, com contexto do `rag` (RAG) | FastAPI + LangChain (LCEL) + OpenAI | 8002 |

Nenhum serviço importa código de negócio de outro — a única comunicação entre eles é via HTTP
(o `chatbot` chama a API do `rag`, best-effort). A única coisa compartilhada é
[`libs/observability`](libs/observability) (logging estruturado), referenciada por cada app como
dependência de path (`../../libs/observability`), não por um workspace comum — não existe
`pyproject.toml` na raiz do repo; cada `apps/*` é instalado/rodado/testado de dentro da sua
própria pasta.

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

- [`uv`](https://docs.astral.sh/uv/) (gerencia cada projeto Python individualmente)
- Docker + Docker Compose (Postgres da `library_api`)
- Uma OpenAI API key (só necessária para o `chatbot` responder de verdade, ou para o `rag` se
  `EMBEDDING_PROVIDER=openai`)

## Setup

Não há um passo de setup único: cada serviço é instalado separadamente, de dentro da sua
própria pasta. Veja o README de cada um para o passo a passo completo:

- [apps/library_api/README.md](apps/library_api/README.md)
- [apps/rag/README.md](apps/rag/README.md)
- [apps/chatbot/README.md](apps/chatbot/README.md)

Resumo rápido (repita para os 3 apps):

```bash
cd apps/<servico>
uv sync
cp .env.example .env   # cada app tem seu próprio .env.example, só com o que ele precisa
```

## Subindo tudo junto

```bash
# 1) Postgres (necessário só para library_api)
docker compose up -d postgres

# 2) library_api — terminal 1
cd apps/library_api && uv run alembic upgrade head && uv run uvicorn library_api.main:app --reload --port 8000

# 3) rag — terminal 2
cd apps/rag && uv run rag ingest && uv run uvicorn rag.main:app --reload --port 8001

# 4) chatbot — terminal 3 (precisa do rag rodando para ter contexto RAG)
cd apps/chatbot && RAG_API_URL=http://localhost:8001 uv run uvicorn chatbot.main:app --reload --port 8002
```

Docs interativas (Swagger) de cada serviço: `http://localhost:8000/api/docs`,
`http://localhost:8001/api/docs`, `http://localhost:8002/api/docs`.

Também é possível interagir com a busca semântica e com o chatbot direto pelo terminal, sem
subir a API HTTP:

```bash
cd apps/rag && uv run rag search "como funciona async/await em python?" --k 3
cd apps/chatbot && uv run chatbot
```

## Variáveis de ambiente

Cada serviço tem seu próprio `.env.example`, isolado com só o que ele precisa — não existe
mais um `.env` único compartilhado por todos:

| `.env.example` | Variáveis | Uso |
|---|---|---|
| [`.env.example`](.env.example) (raiz) | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT` | só o `docker-compose.yml` (Postgres) |
| [`apps/library_api/.env.example`](apps/library_api/.env.example) | `DATABASE_URL`, `DEFAULT_LOAN_PERIOD_DAYS`, `CORS_ALLOWED_ORIGINS`, `LOG_LEVEL`, `LOG_JSON` | API de biblioteca |
| [`apps/rag/.env.example`](apps/rag/.env.example) | `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `OPENAI_API_KEY` (se `EMBEDDING_PROVIDER=openai`), `RAG_DATA_DIR`, `RAG_INDEX_DIR`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `LOG_LEVEL`, `LOG_JSON` | embeddings/busca semântica |
| [`apps/chatbot/.env.example`](apps/chatbot/.env.example) | `OPENAI_API_KEY`, `CHATBOT_MODEL`, `RAG_API_URL`, `RAG_CONTEXT_K`, `LOG_LEVEL`, `LOG_JSON` | chatbot |

`DATABASE_URL` (library_api) precisa bater com as credenciais definidas no `.env` da raiz para
o `docker compose up -d postgres` (usuário/senha/porta/nome do banco).

## Logs estruturados

Todos os serviços usam `libs/observability` para logar em JSON (via `structlog`), com um
`request_id` por requisição (propagado pelo header `X-Request-ID`), latência e eventos de
domínio relevantes (ex: `loan.created`, `rag.search.completed`, `chatbot.answered`):

```json
{"event": "request.finished", "request_id": "...", "status_code": 200, "duration_ms": 12.4, "service": "library_api"}
```

## Testes

```bash
cd apps/library_api && uv run pytest
cd apps/rag && uv run pytest
cd apps/chatbot && uv run pytest
cd libs/observability && uv run pytest
```

Testes unitários não tocam rede/infra externa (mockam OpenAI, chamadas HTTP entre serviços
etc.); testes de integração sobem o app FastAPI real (com `httpx.AsyncClient`) e, na
`library_api`, usam um banco SQLite em memória. `library_api/tests/test_migrations.py` roda
`alembic upgrade head` contra o Postgres real do `docker-compose` (pulado automaticamente se
o Postgres não estiver acessível).

## Documentação do pipeline de embeddings

Veja [docs/embeddings.md](docs/embeddings.md): explica o pipeline completo (ingestão → chunking
→ embedding → indexação FAISS → busca) e mostra exemplos reais de consultas com resultados.
