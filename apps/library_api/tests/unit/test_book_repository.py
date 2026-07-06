from sqlalchemy.ext.asyncio import AsyncSession

from library_api.catalog.adapters.repositories import SqlAlchemyAuthorRepository, SqlAlchemyBookRepository
from library_api.catalog.domain.entities import Author, Book


async def test_get_by_isbn_returns_none_when_missing(session: AsyncSession) -> None:
    repository = SqlAlchemyBookRepository(session)

    assert await repository.get_by_isbn("does-not-exist") is None


async def test_get_by_isbn_finds_existing_book(session: AsyncSession) -> None:
    author = await SqlAlchemyAuthorRepository(session).add(Author(name="Ada Lovelace"))

    repository = SqlAlchemyBookRepository(session)
    await repository.add(
        Book.create(
            title="Clean Code",
            isbn="978-0132350884",
            category="tech",
            author_id=author.id,
            total_copies=2,
        )
    )

    found = await repository.get_by_isbn("978-0132350884")

    assert found is not None
    assert found.title == "Clean Code"
