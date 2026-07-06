from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from library_api.catalog.adapters.repositories import SqlAlchemyBookRepository
from library_api.lending.adapters.repositories import SqlAlchemyLoanRepository, SqlAlchemyMemberRepository
from library_api.lending.service_layer.services import LoanService, MemberService
from library_api.shared.config import Settings, get_settings
from library_api.shared.database import get_db_session

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def get_member_service(session: DbSession) -> MemberService:
    return MemberService(SqlAlchemyMemberRepository(session))


def get_loan_service(session: DbSession, settings: AppSettings) -> LoanService:
    # composition root: aqui (e só aqui) o context `lending` conhece o adapter concreto
    # de `catalog` (SqlAlchemyBookRepository) — o `LoanService` em si só enxerga o port.
    return LoanService(
        SqlAlchemyLoanRepository(session),
        SqlAlchemyBookRepository(session),
        SqlAlchemyMemberRepository(session),
        default_loan_period_days=settings.default_loan_period_days,
    )


MemberServiceDep = Annotated[MemberService, Depends(get_member_service)]
LoanServiceDep = Annotated[LoanService, Depends(get_loan_service)]
