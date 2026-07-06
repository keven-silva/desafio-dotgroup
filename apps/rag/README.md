# rag

Pipeline de ingestão de documentos, geração de embeddings e busca semântica (FAISS), exposto
via CLI e API HTTP. Ver [docs/embeddings.md](../../docs/embeddings.md) na raiz do repositório
para a documentação completa do processo, com exemplos reais de consulta.

Projeto `uv` independente — tem seu próprio `pyproject.toml`/`uv.lock`/`.venv`, sem depender de
workspace com os outros serviços. A única dependência local é `../../libs/observability`
(logging estruturado compartilhado).

## Setup

```bash
cd apps/rag
uv sync
cp .env.example .env   # ajuste EMBEDDING_PROVIDER/EMBEDDING_MODEL se necessário
```

## Uso — CLI

```bash
uv run rag ingest                                            # popula o índice a partir de data/raw/
uv run rag search "como funciona async/await em python?" --k 3
```

## Uso — API HTTP

```bash
uv run uvicorn rag.main:app --reload --port 8001
```

Docs interativas em `http://localhost:8001/api/docs`. Endpoints: `POST /ingest`, `POST /search`.

## Testes

```bash
uv run pytest
```
