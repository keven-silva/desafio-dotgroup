# rag

Pipeline de ingestão de documentos, geração de embeddings e busca semântica (FAISS). Ver [docs/embeddings.md](../../docs/embeddings.md) na raiz do repositório para a documentação completa do processo.

## Uso

```bash
uv run --package rag rag ingest
uv run --package rag rag search "como funciona async/await em python"
```

## Testes

```bash
uv run --package rag pytest
```
