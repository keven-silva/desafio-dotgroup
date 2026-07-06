from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas import (
    AskRequest,
    AskResponse,
    BookCreate,
    BookRead,
    IngestRequest,
    IngestResponse,
)
from app.core.config import settings
from app.core.database import engine, get_db
from app.models.base import Base
from app.services.book_service import BookService
from chatbot.service import PythonDevChatbot
from vector_store.service import VectorStoreService


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_create_schema:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
chatbot = PythonDevChatbot()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/books", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, db: Session = Depends(get_db)) -> BookRead:
    service = BookService(db)
    return service.create(payload)


@app.get("/books", response_model=list[BookRead])
def list_books(db: Session = Depends(get_db)) -> list[BookRead]:
    service = BookService(db)
    return service.list()


@app.get("/books/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)) -> BookRead:
    service = BookService(db)
    book = service.get(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@app.post("/chatbot/ask", response_model=AskResponse)
def ask_chatbot(payload: AskRequest) -> AskResponse:
    return AskResponse(answer=chatbot.answer(payload.question))


@app.post("/vector-store/ingest", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_document(payload: IngestRequest, db: Session = Depends(get_db)) -> IngestResponse:
    service = VectorStoreService(db)
    stored = service.ingest(source=payload.source, content=payload.content)
    return IngestResponse(id=stored.id, dimensions=len(stored.embedding))
