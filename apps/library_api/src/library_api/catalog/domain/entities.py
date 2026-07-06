from dataclasses import dataclass

from library_api.catalog.domain.exceptions import BookNotAvailableError


@dataclass
class Author:
    name: str
    bio: str | None = None
    id: int | None = None


@dataclass
class Book:
    """Aggregate root do catálogo: garante que cópias disponíveis nunca ficam inconsistentes."""

    title: str
    isbn: str
    category: str
    author_id: int
    total_copies: int
    available_copies: int
    id: int | None = None

    @classmethod
    def create(cls, *, title: str, isbn: str, category: str, author_id: int, total_copies: int) -> "Book":
        return cls(
            title=title,
            isbn=isbn,
            category=category,
            author_id=author_id,
            total_copies=total_copies,
            available_copies=total_copies,
        )

    def check_out(self) -> None:
        if self.available_copies < 1:
            raise BookNotAvailableError(f"Livro {self.id} não possui cópias disponíveis")
        self.available_copies -= 1

    def check_in(self) -> None:
        self.available_copies = min(self.total_copies, self.available_copies + 1)

    def change_total_copies(self, new_total: int) -> None:
        delta = new_total - self.total_copies
        self.total_copies = new_total
        self.available_copies = max(0, min(new_total, self.available_copies + delta))
