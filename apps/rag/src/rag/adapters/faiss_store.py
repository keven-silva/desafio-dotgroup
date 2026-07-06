import json
from pathlib import Path

import faiss
import numpy as np

from rag.domain.entities import Chunk, SearchResult


class FaissVectorStore:
    """Implementa `VectorStore` com um índice FAISS (`IndexFlatIP`, vetores normalizados
    => produto interno equivale a similaridade de cosseno) persistido em disco."""

    INDEX_FILENAME = "faiss.index"
    METADATA_FILENAME = "metadata.json"

    def __init__(self, index_dir: Path, dimension: int) -> None:
        self._index_dir = index_dir
        self._dimension = dimension
        self._index = faiss.IndexFlatIP(dimension)
        self._chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if not chunks:
            return
        matrix = np.asarray(vectors, dtype="float32")
        self._index.add(matrix)
        self._chunks.extend(chunks)

    def search(self, query_vector: list[float], k: int) -> list[SearchResult]:
        if self._index.ntotal == 0:
            return []
        query = np.asarray([query_vector], dtype="float32")
        scores, indices = self._index.search(query, min(k, self._index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0], strict=True):
            if idx < 0:
                continue
            chunk = self._chunks[idx]
            results.append(SearchResult(text=chunk.text, source=chunk.source, score=float(score)))
        return results

    def save(self) -> None:
        self._index_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(self._index_dir / self.INDEX_FILENAME))
        metadata = [{"text": c.text, "source": c.source, "chunk_index": c.chunk_index} for c in self._chunks]
        (self._index_dir / self.METADATA_FILENAME).write_text(json.dumps(metadata), encoding="utf-8")

    def load(self) -> bool:
        index_path = self._index_dir / self.INDEX_FILENAME
        metadata_path = self._index_dir / self.METADATA_FILENAME
        if not index_path.exists() or not metadata_path.exists():
            return False

        self._index = faiss.read_index(str(index_path))
        raw_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self._chunks = [
            Chunk(text=item["text"], source=item["source"], chunk_index=item["chunk_index"])
            for item in raw_metadata
        ]
        return True
