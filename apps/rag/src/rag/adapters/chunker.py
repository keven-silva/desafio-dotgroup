from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.domain.entities import Chunk, Document


def chunk_documents(documents: list[Document], *, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    chunks: list[Chunk] = []
    for document in documents:
        for index, text in enumerate(splitter.split_text(document.text)):
            chunks.append(Chunk(text=text, source=document.source, chunk_index=index))
    return chunks
