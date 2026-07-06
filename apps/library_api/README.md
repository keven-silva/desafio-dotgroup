# library_api

API REST de biblioteca: autores, livros, membros e empréstimos.

## Rodar localmente

```bash
docker compose up -d postgres          # a partir da raiz do repo
uv run --package library-api alembic upgrade head
uv run --package library-api uvicorn library_api.main:app --reload
```

Docs interativas em `http://localhost:8000/docs`.

## Testes

```bash
uv run --package library-api pytest
```
