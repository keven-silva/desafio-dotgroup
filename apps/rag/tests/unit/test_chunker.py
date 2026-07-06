from rag.adapters.chunker import chunk_documents
from rag.domain.entities import Document


def test_chunk_documents_splits_long_text_into_multiple_chunks() -> None:
    long_text = "Python é uma linguagem de programação. " * 100
    documents = [Document(source="a.md", text=long_text)]

    chunks = chunk_documents(documents, chunk_size=200, chunk_overlap=20)

    assert len(chunks) > 1
    assert all(chunk.source == "a.md" for chunk in chunks)
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))


def test_chunk_documents_keeps_short_text_as_single_chunk() -> None:
    documents = [Document(source="b.md", text="Texto curto.")]

    chunks = chunk_documents(documents, chunk_size=800, chunk_overlap=120)

    assert len(chunks) == 1
    assert chunks[0].text == "Texto curto."
    assert chunks[0].source == "b.md"


def test_chunk_documents_handles_multiple_documents_independently() -> None:
    documents = [
        Document(source="a.md", text="Conteúdo do primeiro documento."),
        Document(source="b.md", text="Conteúdo do segundo documento."),
    ]

    chunks = chunk_documents(documents, chunk_size=800, chunk_overlap=0)

    sources = {chunk.source for chunk in chunks}
    assert sources == {"a.md", "b.md"}
