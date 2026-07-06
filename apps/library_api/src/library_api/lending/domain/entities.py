from dataclasses import dataclass
from datetime import datetime, timedelta

from library_api.lending.domain.exceptions import LoanAlreadyReturnedError


@dataclass
class Member:
    name: str
    email: str
    id: int | None = None


@dataclass
class Loan:
    """Aggregate root de empréstimo: garante que não é devolvido duas vezes."""

    book_id: int
    member_id: int
    loaned_at: datetime
    due_at: datetime
    returned_at: datetime | None = None
    id: int | None = None

    @classmethod
    def open(cls, *, book_id: int, member_id: int, loaned_at: datetime, period_days: int) -> "Loan":
        return cls(
            book_id=book_id,
            member_id=member_id,
            loaned_at=loaned_at,
            due_at=loaned_at + timedelta(days=period_days),
        )

    def mark_returned(self, when: datetime) -> None:
        if self.returned_at is not None:
            raise LoanAlreadyReturnedError(f"Empréstimo {self.id} já foi devolvido")
        self.returned_at = when
