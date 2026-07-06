# library_api

API REST de biblioteca: autores, livros, membros e empréstimos (FastAPI + SQLAlchemy async +
PostgreSQL + Alembic), organizada em dois bounded contexts (`catalog` e `lending`).

Projeto `uv` independente — tem seu próprio `pyproject.toml`/`uv.lock`/`.venv`, sem depender de
workspace com os outros serviços. A única dependência local é `../../libs/observability`
(logging estruturado compartilhado).

## Setup

```bash
cd apps/library_api
uv sync
cp .env.example .env   # ajuste DATABASE_URL/CORS_ALLOWED_ORIGINS se necessário
```

## Rodar localmente

```bash
docker compose -f ../../docker-compose.yml up -d postgres   # a partir desta pasta
uv run alembic upgrade head
uv run uvicorn library_api.main:app --reload --port 8000
```

Docs interativas em `http://localhost:8000/api/docs`.

## Testes

```bash
uv run pytest
```

`tests/test_migrations.py` roda `alembic upgrade head` contra o Postgres real (pulado
automaticamente se o Postgres não estiver acessível). Os demais testes usam SQLite em memória.
