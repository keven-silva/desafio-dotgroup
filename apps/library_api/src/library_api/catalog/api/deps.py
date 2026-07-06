from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from library_api.catalog.adapters.repositories import SqlAlchemyAuthorRepository, SqlAlchemyBookRepository
from library_api.catalog.service_layer.services import AuthorService, BookService
from library_api.shared.database import get_db_session

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_author_service(session: DbSession) -> AuthorService:
    return AuthorService(SqlAlchemyAuthorRepository(session))


def get_book_service(session: DbSession) -> BookService:
    return BookService(SqlAlchemyBookRepository(session))


AuthorServiceDep = Annotated[AuthorService, Depends(get_author_service)]
BookServiceDep = Annotated[BookService, Depends(get_book_service)]
