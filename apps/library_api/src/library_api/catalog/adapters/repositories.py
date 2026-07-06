from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from library_api.catalog.adapters.orm import AuthorModel, BookModel
from library_api.catalog.domain.entities import Author, Book


def _author_to_entity(model: AuthorModel) -> Author:
    return Author(id=model.id, name=model.name, bio=model.bio)


def _apply_author(entity: Author, model: AuthorModel) -> AuthorModel:
    model.name = entity.name
    model.bio = entity.bio
    return model


def _book_to_entity(model: BookModel) -> Book:
    return Book(
        id=model.id,
        title=model.title,
        isbn=model.isbn,
        category=model.category,
        author_id=model.author_id,
        total_copies=model.total_copies,
        available_copies=model.available_copies,
    )


def _apply_book(entity: Book, model: BookModel) -> BookModel:
    model.title = entity.title
    model.isbn = entity.isbn
    model.category = entity.category
    model.author_id = entity.author_id
    model.total_copies = entity.total_copies
    model.available_copies = entity.available_copies
    return model


class SqlAlchemyAuthorRepository:
    """Implementa `catalog.domain.ports.AuthorRepository` mapeando `AuthorModel` <-> `Author`."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, id_: int) -> Author | None:
        model = await self._session.get(AuthorModel, id_)
        return _author_to_entity(model) if model else None

    async def list(self, *, offset: int = 0, limit: int = 100) -> Sequence[Author]:
        result = await self._session.execute(select(AuthorModel).offset(offset).limit(limit))
        return [_author_to_entity(m) for m in result.scalars().all()]

    async def add(self, author: Author) -> Author:
        model = _apply_author(author, AuthorModel())
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _author_to_entity(model)

    async def update(self, author: Author) -> Author:
        model = await self._session.get(AuthorModel, author.id)
        assert model is not None, f"Author {author.id} não existe para atualizar"
        _apply_author(author, model)
        await self._session.flush()
        return _author_to_entity(model)

    async def delete(self, author: Author) -> None:
        model = await self._session.get(AuthorModel, author.id)
        if model is not None:
            await self._session.delete(model)
            await self._session.flush()


class SqlAlchemyBookRepository:
    """Implementa `catalog.domain.ports.BookRepository` mapeando `BookModel` <-> `Book`."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, id_: int) -> Book | None:
        model = await self._session.get(BookModel, id_)
        return _book_to_entity(model) if model else None

    async def get_by_isbn(self, isbn: str) -> Book | None:
        result = await self._session.execute(select(BookModel).where(BookModel.isbn == isbn))
        model = result.scalar_one_or_none()
        return _book_to_entity(model) if model else None

    async def list(self, *, offset: int = 0, limit: int = 100) -> Sequence[Book]:
        result = await self._session.execute(select(BookModel).offset(offset).limit(limit))
        return [_book_to_entity(m) for m in result.scalars().all()]

    async def add(self, book: Book) -> Book:
        model = _apply_book(book, BookModel())
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _book_to_entity(model)

    async def update(self, book: Book) -> Book:
        model = await self._session.get(BookModel, book.id)
        assert model is not None, f"Book {book.id} não existe para atualizar"
        _apply_book(book, model)
        await self._session.flush()
        return _book_to_entity(model)

    async def delete(self, book: Book) -> None:
        model = await self._session.get(BookModel, book.id)
        if model is not None:
            await self._session.delete(model)
            await self._session.flush()
