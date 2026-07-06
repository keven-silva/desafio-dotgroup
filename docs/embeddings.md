# Pipeline de embeddings e busca semântica (`rag`)

Este documento explica como o serviço `rag` (`apps/rag`) transforma artigos/posts em texto
puro em um índice pesquisável por similaridade semântica, e mostra exemplos reais de consulta.

## Visão geral do pipeline

```
data/raw/*.md,*.txt  ──►  load_documents()  ──►  chunk_documents()  ──►  embedding_strategy.embed()  ──►  FaissVectorStore
     (Document)              (Document)              (Chunk)                 (vetores)                (persistido em disco)
```

1. **Carregamento** (`rag.adapters.loader.load_documents`): lê todo arquivo `.md`/`.txt` de
   `apps/rag/data/raw/` e monta um `Document` (`source` = nome do arquivo, `text` = conteúdo).
2. **Chunking** (`rag.adapters.chunker.chunk_documents`): usa o `RecursiveCharacterTextSplitter`
   do `langchain-text-splitters` para dividir cada documento em pedaços de até `chunk_size`
   caracteres (com `chunk_overlap` caracteres de sobreposição entre pedaços consecutivos),
   gerando `Chunk`s — a unidade que de fato vira embedding.
3. **Embedding** (`rag.domain.ports.EmbeddingStrategy`, Strategy Pattern): cada `Chunk.text` é
   convertido em um vetor numérico. Duas estratégias implementam a mesma interface
   (`embed(texts) -> vetores`), trocáveis por config (`EMBEDDING_PROVIDER`):
   - `sentence-transformers` (`rag.adapters.sentence_transformers_strategy`): modelo local,
     sem custo, sem depender de API externa.
   - `openai` (`rag.adapters.openai_strategy`): usa a API de embeddings da OpenAI (pago).
4. **Indexação** (`rag.adapters.faiss_store.FaissVectorStore`): os vetores (normalizados) são
   inseridos num `faiss.IndexFlatIP` — produto interno de vetores normalizados equivale a
   similaridade de cosseno — e o índice + metadados (texto/fonte de cada chunk) são persistidos
   em `apps/rag/data/index/` (`faiss.index` + `metadata.json`).
5. **Busca** (`rag.service_layer.services.semantic_search`): a query do usuário passa pela
   mesma `embedding_strategy`, e o vetor resultante é comparado contra o índice FAISS,
   retornando os `k` chunks mais similares com seus scores.

Todo esse pipeline é exposto de duas formas equivalentes (mesmo `service_layer`, duas portas
de entrada):
- **CLI**: `uv run --package rag rag ingest` e `uv run --package rag rag search "pergunta" --k 3`.
- **API HTTP**: `POST /ingest` e `POST /search {"query": "...", "k": 3}` (serviço roda em
  `uv run --package rag uvicorn rag.main:app --port 8001`).

## Escolha do modelo de embedding

O modelo local padrão é o `paraphrase-multilingual-MiniLM-L12-v2` (via `sentence-transformers`).
Isso foi validado empiricamente: o modelo `all-MiniLM-L6-v2` (mais comum em exemplos em inglês)
rankeia mal consultas em português — nos testes durante o desenvolvimento, uma pergunta sobre
"programação assíncrona em Python" recuperava um artigo sobre gerenciamento de dependências
como resultado mais relevante, porque o modelo não foi treinado para capturar nuances
semânticas em PT-BR. Trocando para um modelo multilíngue, a mesma consulta passou a recuperar
corretamente o artigo sobre `async`/`await` como top-1. Como a escolha do provedor/modelo é um
Strategy Pattern configurável (`EMBEDDING_PROVIDER`/`EMBEDDING_MODEL` no `.env`), essa troca não
exigiu nenhuma mudança no pipeline (`chunker`, `service_layer`, `faiss_store`).

## Exemplos reais de busca semântica

Índice construído a partir de 4 artigos de exemplo em `apps/rag/data/raw/` (async/await,
type hints, ambientes virtuais, injeção de dependências no FastAPI) — 14 chunks no total.

### Consulta: "como funciona programação assíncrona em python?"

```
[1] score=0.6548 source=async-await.md
    # Programação assíncrona com async/await em Python
    Python oferece suporte nativo a programação assíncrona através das palavras-chave `async`
    e `await`, introduzidas de forma completa a partir do módulo `asyncio`...

[2] score=0.6275 source=type-hints.md
    # Type hints e tipagem estática em Python...
```

### Consulta: "como o FastAPI resolve dependências entre camadas?"

```
[1] score=0.6890 source=fastapi-dependency-injection.md
    # Injeção de dependências no FastAPI
    O sistema de dependências do FastAPI, exposto através da função `Depends`, é um dos recursos
    mais poderosos do framework...
```

### Consulta: "como isolar dependências de um projeto Python?"

```
[1] score=0.7917 source=virtualenv-e-gerenciamento-de-dependencias.md
    # Ambientes virtuais e gerenciamento de dependências em Python
    Um dos problemas centrais ao trabalhar com Python é isolar as dependências de cada projeto...
```

Em todos os casos, o chunk mais relevante (maior score) corresponde exatamente ao artigo cujo
assunto casa com a pergunta — validando que o pipeline de embeddings + FAISS está recuperando
resultados semanticamente corretos, e não apenas por correspondência literal de palavras (nenhuma
das queries repete o título do artigo palavra por palavra).

## Reproduzindo os exemplos

```bash
cd desafio-dotgroup
uv run --package rag rag ingest
uv run --package rag rag search "como funciona programação assíncrona em python?" --k 2
uv run --package rag rag search "como o FastAPI resolve dependências entre camadas?" --k 1
uv run --package rag rag search "como isolar dependências de um projeto Python?" --k 1
```
