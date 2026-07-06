from sqlalchemy.orm import Session

from app.models.document_embedding import DocumentEmbedding
from vector_store.embeddings import EmbeddingGenerator


class VectorStoreService:
    def __init__(self, db: Session, generator: EmbeddingGenerator | None = None) -> None:
        self.db = db
        self.generator = generator or EmbeddingGenerator()

    def ingest(self, source: str, content: str) -> DocumentEmbedding:
        embedding = self.generator.embed(content)
        item = DocumentEmbedding(source=source, content=content, embedding=embedding)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
