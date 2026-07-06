from collections.abc import Sequence
from datetime import UTC, datetime

from observability import get_logger

from library_api.catalog.domain.ports import BookRepository
from library_api.lending.domain.entities import Loan, Member
from library_api.lending.domain.ports import LoanRepository, MemberRepository
from library_api.shared.exceptions import ConflictError, NotFoundError

logger = get_logger()


class MemberService:
    def __init__(self, repository: MemberRepository) -> None:
        self._repository = repository

    async def create(self, *, name: str, email: str) -> Member:
        if await self._repository.get_by_email(email) is not None:
            raise ConflictError(f"Já existe um membro com o e-mail {email}")
        return await self._repository.add(Member(name=name, email=email))

    async def get(self, member_id: int) -> Member:
        member = await self._repository.get(member_id)
        if member is None:
            raise NotFoundError(f"Membro {member_id} não encontrado")
        return member

    async def list(self, *, offset: int = 0, limit: int = 100) -> Sequence[Member]:
        return await self._repository.list(offset=offset, limit=limit)

    async def update(self, member_id: int, *, name: str | None = None) -> Member:
        member = await self.get(member_id)
        if name is not None:
            member.name = name
        return await self._repository.update(member)

    async def delete(self, member_id: int) -> None:
        member = await self.get(member_id)
        await self._repository.delete(member)


class LoanService:
    """Orquestra o aggregate `Loan` (lending) e o aggregate `Book` (catalog) via suas portas.

    A colaboração entre bounded contexts acontece só através de `BookRepository` (o port do
    catalog), nunca importando `catalog.adapters` diretamente — quem decide a implementação
    concreta é o `deps.py` (composition root), não o service.
    """

    def __init__(
        self,
        loan_repository: LoanRepository,
        book_repository: BookRepository,
        member_repository: MemberRepository,
        default_loan_period_days: int = 14,
    ) -> None:
        self._loans = loan_repository
        self._books = book_repository
        self._members = member_repository
        self._default_loan_period_days = default_loan_period_days

    async def loan_book(self, *, book_id: int, member_id: int) -> Loan:
        book = await self._books.get(book_id)
        if book is None:
            raise NotFoundError(f"Livro {book_id} não encontrado")

        member = await self._members.get(member_id)
        if member is None:
            raise NotFoundError(f"Membro {member_id} não encontrado")

        book.check_out()  # invariante do aggregate Book (catalog) — pode levantar BookNotAvailableError

        loan = Loan.open(
            book_id=book.id,
            member_id=member.id,
            loaned_at=datetime.now(UTC),
            period_days=self._default_loan_period_days,
        )

        await self._books.update(book)
        loan = await self._loans.add(loan)

        logger.info("loan.created", loan_id=loan.id, book_id=book.id, member_id=member.id)
        return loan

    async def return_book(self, loan_id: int) -> Loan:
        loan = await self._loans.get(loan_id)
        if loan is None:
            raise NotFoundError(f"Empréstimo {loan_id} não encontrado")

        book = await self._books.get(loan.book_id)
        if book is None:
            raise NotFoundError(f"Livro {loan.book_id} não encontrado")

        loan.mark_returned(datetime.now(UTC))  # pode levantar LoanAlreadyReturnedError
        book.check_in()

        await self._books.update(book)
        loan = await self._loans.update(loan)

        logger.info("loan.returned", loan_id=loan.id, book_id=book.id)
        return loan

    async def get(self, loan_id: int) -> Loan:
        loan = await self._loans.get(loan_id)
        if loan is None:
            raise NotFoundError(f"Empréstimo {loan_id} não encontrado")
        return loan

    async def list(self, *, offset: int = 0, limit: int = 100) -> Sequence[Loan]:
        return await self._loans.list(offset=offset, limit=limit)
