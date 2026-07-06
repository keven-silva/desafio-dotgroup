import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from library_api.catalog.adapters.repositories import SqlAlchemyAuthorRepository
from library_api.catalog.service_layer.services import AuthorService
from library_api.shared.exceptions import ConflictError


def _make_service(session: AsyncSession) -> AuthorService:
    return AuthorService(SqlAlchemyAuthorRepository(session))


async def test_create_author_raises_on_duplicate_name(session: AsyncSession) -> None:
    service = _make_service(session)
    await service.create(name="Robert C. Martin")

    with pytest.raises(ConflictError):
        await service.create(name="Robert C. Martin")


async def test_create_author_raises_on_duplicate_name_regardless_of_case(session: AsyncSession) -> None:
    service = _make_service(session)
    await service.create(name="Robert C. Martin")

    with pytest.raises(ConflictError):
        await service.create(name="ROBERT C. MARTIN")


async def test_update_author_raises_when_renaming_to_existing_name(session: AsyncSession) -> None:
    service = _make_service(session)
    await service.create(name="Robert C. Martin")
    other = await service.create(name="Ada Lovelace")

    with pytest.raises(ConflictError):
        await service.update(other.id, name="robert c. martin")


async def test_update_author_allows_keeping_its_own_name_with_different_case(session: AsyncSession) -> None:
    service = _make_service(session)
    author = await service.create(name="Robert C. Martin")

    updated = await service.update(author.id, name="Robert C. Martin", bio="novo bio")

    assert updated.bio == "novo bio"
