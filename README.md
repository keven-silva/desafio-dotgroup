# desafio-dotgroup

Projeto estruturado em 3 frentes:

## 1) API (FastAPI + SQLAlchemy + PostgreSQL + Alembic)
- Endpoints de biblioteca:
  - `POST /books`
  - `GET /books`
  - `GET /books/{id}`
- Healthcheck:
  - `GET /health`
- Migrações com Alembic em `alembic/versions`.

## 2) Chatbot para desenvolvimento Python
- Endpoint:
  - `POST /chatbot/ask`
- Serviço com respostas orientadas a boas práticas Python (DRY/SOLID, FastAPI, SQLAlchemy, testes).

## 3) Vector store e embeddings
- Endpoint:
  - `POST /vector-store/ingest`
- Ingestão de conteúdo de artigos/posts com geração de embedding e persistência no banco.

## Como executar
```bash
pip install -e .
uvicorn app.main:app --reload
```

## Migrações
```bash
alembic upgrade head
```