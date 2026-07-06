from sqlalchemy.orm import Session

from app.api.schemas import BookCreate
from app.models.book import Book


class BookService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: BookCreate) -> Book:
        book = Book(title=payload.title, author=payload.author)
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def list(self) -> list[Book]:
        return self.db.query(Book).order_by(Book.id).all()

    def get(self, book_id: int) -> Book | None:
        return self.db.get(Book, book_id)
