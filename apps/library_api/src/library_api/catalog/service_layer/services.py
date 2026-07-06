from collections.abc import Sequence

from library_api.catalog.domain.entities import Author, Book
from library_api.catalog.domain.ports import AuthorRepository, BookRepository
from library_api.shared.exceptions import ConflictError, NotFoundError


class AuthorService:
    def __init__(self, repository: AuthorRepository) -> None:
        self._repository = repository

    async def create(self, *, name: str, bio: str | None = None) -> Author:
        return await self._repository.add(Author(name=name, bio=bio))

    async def get(self, author_id: int) -> Author:
        author = await self._repository.get(author_id)
        if author is None:
            raise NotFoundError(f"Autor {author_id} não encontrado")
        return author

    async def list(self, *, offset: int = 0, limit: int = 100) -> Sequence[Author]:
        return await self._repository.list(offset=offset, limit=limit)

    async def update(self, author_id: int, *, name: str | None = None, bio: str | None = None) -> Author:
        author = await self.get(author_id)
        if name is not None:
            author.name = name
        if bio is not None:
            author.bio = bio
        return await self._repository.update(author)

    async def delete(self, author_id: int) -> None:
        author = await self.get(author_id)
        await self._repository.delete(author)


class BookService:
    def __init__(self, repository: BookRepository) -> None:
        self._repository = repository

    async def create(
        self, *, title: str, isbn: str, category: str, author_id: int, total_copies: int
    ) -> Book:
        if await self._repository.get_by_isbn(isbn) is not None:
            raise ConflictError(f"Já existe um livro com ISBN {isbn}")
        book = Book.create(
            title=title, isbn=isbn, category=category, author_id=author_id, total_copies=total_copies
        )
        return await self._repository.add(book)

    async def get(self, book_id: int) -> Book:
        book = await self._repository.get(book_id)
        if book is None:
            raise NotFoundError(f"Livro {book_id} não encontrado")
        return book

    async def list(self, *, offset: int = 0, limit: int = 100) -> Sequence[Book]:
        return await self._repository.list(offset=offset, limit=limit)

    async def update(
        self,
        book_id: int,
        *,
        title: str | None = None,
        category: str | None = None,
        total_copies: int | None = None,
    ) -> Book:
        book = await self.get(book_id)
        if total_copies is not None:
            book.change_total_copies(total_copies)
        if title is not None:
            book.title = title
        if category is not None:
            book.category = category
        return await self._repository.update(book)

    async def delete(self, book_id: int) -> None:
        book = await self.get(book_id)
        await self._repository.delete(book)
