from fastapi import APIRouter, status

from library_api.catalog.service_layer.services import BookService
from library_api.lending.api.deps import BookServiceDep, LoanServiceDep, MemberServiceDep
from library_api.lending.api.schemas import LoanCreate, LoanRead, MemberCreate, MemberRead, MemberUpdate
from library_api.lending.domain.entities import Loan
from library_api.lending.service_layer.services import MemberService

router = APIRouter()

members_router = APIRouter(prefix="/members", tags=["members"])
loans_router = APIRouter(prefix="/loans", tags=["loans"])


async def _to_loan_read(loan: Loan, book_service: BookService, member_service: MemberService) -> LoanRead:
    book = await book_service.get(loan.book_id)
    member = await member_service.get(loan.member_id)
    return LoanRead(
        id=loan.id,
        book_id=loan.book_id,
        book_title=book.title,
        member_id=loan.member_id,
        member_name=member.name,
        loaned_at=loan.loaned_at,
        due_at=loan.due_at,
        returned_at=loan.returned_at,
    )


@members_router.post("", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
async def create_member(data: MemberCreate, service: MemberServiceDep) -> MemberRead:
    return await service.create(name=data.name, email=data.email)


@members_router.get("", response_model=list[MemberRead])
async def list_members(service: MemberServiceDep, offset: int = 0, limit: int = 100) -> list[MemberRead]:
    return list(await service.list(offset=offset, limit=limit))


@members_router.get("/{member_id}", response_model=MemberRead)
async def get_member(member_id: int, service: MemberServiceDep) -> MemberRead:
    return await service.get(member_id)


@members_router.patch("/{member_id}", response_model=MemberRead)
async def update_member(member_id: int, data: MemberUpdate, service: MemberServiceDep) -> MemberRead:
    return await service.update(member_id, name=data.name)


@members_router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(member_id: int, service: MemberServiceDep) -> None:
    await service.delete(member_id)


@loans_router.post("", response_model=LoanRead, status_code=status.HTTP_201_CREATED)
async def create_loan(
    data: LoanCreate, service: LoanServiceDep, book_service: BookServiceDep, member_service: MemberServiceDep
) -> LoanRead:
    loan = await service.loan_book(book_id=data.book_id, member_id=data.member_id)
    return await _to_loan_read(loan, book_service, member_service)


@loans_router.post("/{loan_id}/return", response_model=LoanRead)
async def return_loan(
    loan_id: int, service: LoanServiceDep, book_service: BookServiceDep, member_service: MemberServiceDep
) -> LoanRead:
    loan = await service.return_book(loan_id)
    return await _to_loan_read(loan, book_service, member_service)


@loans_router.get("", response_model=list[LoanRead])
async def list_loans(
    service: LoanServiceDep,
    book_service: BookServiceDep,
    member_service: MemberServiceDep,
    offset: int = 0,
    limit: int = 100,
) -> list[LoanRead]:
    loans = await service.list(offset=offset, limit=limit)
    return [await _to_loan_read(loan, book_service, member_service) for loan in loans]


@loans_router.get("/{loan_id}", response_model=LoanRead)
async def get_loan(
    loan_id: int, service: LoanServiceDep, book_service: BookServiceDep, member_service: MemberServiceDep
) -> LoanRead:
    loan = await service.get(loan_id)
    return await _to_loan_read(loan, book_service, member_service)


router.include_router(members_router)
router.include_router(loans_router)
