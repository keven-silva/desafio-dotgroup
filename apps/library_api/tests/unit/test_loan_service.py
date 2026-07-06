import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from library_api.catalog.adapters.repositories import SqlAlchemyAuthorRepository, SqlAlchemyBookRepository
from library_api.catalog.domain.entities import Author, Book
from library_api.catalog.domain.exceptions import BookNotAvailableError
from library_api.lending.adapters.repositories import SqlAlchemyLoanRepository, SqlAlchemyMemberRepository
from library_api.lending.domain.entities import Member
from library_api.lending.domain.exceptions import LoanAlreadyReturnedError
from library_api.lending.service_layer.services import LoanService


async def _make_service(session: AsyncSession) -> LoanService:
    return LoanService(
        SqlAlchemyLoanRepository(session), SqlAlchemyBookRepository(session), SqlAlchemyMemberRepository(session)
    )


async def _make_book(session: AsyncSession, *, total_copies: int = 1) -> Book:
    author = await SqlAlchemyAuthorRepository(session).add(Author(name="Autor Teste"))
    return await SqlAlchemyBookRepository(session).add(
        Book.create(
            title="Livro Teste",
            isbn=f"isbn-{total_copies}-{id(session)}",
            category="tech",
            author_id=author.id,
            total_copies=total_copies,
        )
    )


async def _make_member(session: AsyncSession) -> Member:
    return await SqlAlchemyMemberRepository(session).add(
        Member(name="Membro Teste", email=f"m{id(session)}@test.com")
    )


async def test_loan_book_decrements_available_copies(session: AsyncSession) -> None:
    book = await _make_book(session, total_copies=1)
    member = await _make_member(session)
    service = await _make_service(session)

    loan = await service.loan_book(book_id=book.id, member_id=member.id)

    assert loan.id is not None
    assert loan.returned_at is None

    refreshed_book = await SqlAlchemyBookRepository(session).get(book.id)
    assert refreshed_book is not None
    assert refreshed_book.available_copies == 0


async def test_loan_book_raises_when_no_copies_available(session: AsyncSession) -> None:
    book = await _make_book(session, total_copies=0)
    member = await _make_member(session)
    service = await _make_service(session)

    with pytest.raises(BookNotAvailableError):
        await service.loan_book(book_id=book.id, member_id=member.id)


async def test_return_book_increments_available_copies(session: AsyncSession) -> None:
    book = await _make_book(session, total_copies=1)
    member = await _make_member(session)
    service = await _make_service(session)

    loan = await service.loan_book(book_id=book.id, member_id=member.id)
    returned = await service.return_book(loan.id)

    assert returned.returned_at is not None

    refreshed_book = await SqlAlchemyBookRepository(session).get(book.id)
    assert refreshed_book is not None
    assert refreshed_book.available_copies == 1


async def test_return_book_twice_raises(session: AsyncSession) -> None:
    book = await _make_book(session, total_copies=1)
    member = await _make_member(session)
    service = await _make_service(session)

    loan = await service.loan_book(book_id=book.id, member_id=member.id)
    await service.return_book(loan.id)

    with pytest.raises(LoanAlreadyReturnedError):
        await service.return_book(loan.id)
