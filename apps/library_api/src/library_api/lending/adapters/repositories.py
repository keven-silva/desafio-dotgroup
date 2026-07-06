from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from library_api.lending.adapters.orm import LoanModel, MemberModel
from library_api.lending.domain.entities import Loan, Member


def _member_to_entity(model: MemberModel) -> Member:
    return Member(id=model.id, name=model.name, email=model.email)


def _apply_member(entity: Member, model: MemberModel) -> MemberModel:
    model.name = entity.name
    model.email = entity.email
    return model


def _loan_to_entity(model: LoanModel) -> Loan:
    return Loan(
        id=model.id,
        book_id=model.book_id,
        member_id=model.member_id,
        loaned_at=model.loaned_at,
        due_at=model.due_at,
        returned_at=model.returned_at,
    )


def _apply_loan(entity: Loan, model: LoanModel) -> LoanModel:
    model.book_id = entity.book_id
    model.member_id = entity.member_id
    model.loaned_at = entity.loaned_at
    model.due_at = entity.due_at
    model.returned_at = entity.returned_at
    return model


class SqlAlchemyMemberRepository:
    """Implementa `lending.domain.ports.MemberRepository` mapeando `MemberModel` <-> `Member`."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, id_: int) -> Member | None:
        model = await self._session.get(MemberModel, id_)
        return _member_to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Member | None:
        result = await self._session.execute(select(MemberModel).where(MemberModel.email == email))
        model = result.scalar_one_or_none()
        return _member_to_entity(model) if model else None

    async def list(self, *, offset: int = 0, limit: int = 100) -> Sequence[Member]:
        result = await self._session.execute(select(MemberModel).offset(offset).limit(limit))
        return [_member_to_entity(m) for m in result.scalars().all()]

    async def add(self, member: Member) -> Member:
        model = _apply_member(member, MemberModel())
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _member_to_entity(model)

    async def update(self, member: Member) -> Member:
        model = await self._session.get(MemberModel, member.id)
        assert model is not None, f"Member {member.id} não existe para atualizar"
        _apply_member(member, model)
        await self._session.flush()
        return _member_to_entity(model)

    async def delete(self, member: Member) -> None:
        model = await self._session.get(MemberModel, member.id)
        if model is not None:
            await self._session.delete(model)
            await self._session.flush()


class SqlAlchemyLoanRepository:
    """Implementa `lending.domain.ports.LoanRepository` mapeando `LoanModel` <-> `Loan`."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, id_: int) -> Loan | None:
        model = await self._session.get(LoanModel, id_)
        return _loan_to_entity(model) if model else None

    async def list(self, *, offset: int = 0, limit: int = 100) -> Sequence[Loan]:
        result = await self._session.execute(select(LoanModel).offset(offset).limit(limit))
        return [_loan_to_entity(m) for m in result.scalars().all()]

    async def add(self, loan: Loan) -> Loan:
        model = _apply_loan(loan, LoanModel())
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _loan_to_entity(model)

    async def update(self, loan: Loan) -> Loan:
        model = await self._session.get(LoanModel, loan.id)
        assert model is not None, f"Loan {loan.id} não existe para atualizar"
        _apply_loan(loan, model)
        await self._session.flush()
        return _loan_to_entity(model)
