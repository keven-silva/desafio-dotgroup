from pathlib import Path

from rag.domain.entities import Document

SUPPORTED_EXTENSIONS = (".txt", ".md")


def load_documents(data_dir: Path) -> list[Document]:
    """Lê todos os artigos/posts (.txt/.md) de `data_dir` como `Document`s."""
    if not data_dir.exists():
        return []

    documents = []
    for path in sorted(data_dir.iterdir()):
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8").strip()
        if text:
            documents.append(Document(source=path.name, text=text))
    return documents
