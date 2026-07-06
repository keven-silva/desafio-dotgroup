from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    """Um artigo/post de origem, identificado pelo caminho de onde foi lido."""

    source: str
    text: str


@dataclass(frozen=True)
class Chunk:
    """Um pedaço de um `Document`, unidade que de fato vira embedding (value object)."""

    text: str
    source: str
    chunk_index: int


@dataclass(frozen=True)
class SearchResult:
    """Resultado de uma busca semântica: um chunk + sua similaridade com a query."""

    text: str
    source: str
    score: float
