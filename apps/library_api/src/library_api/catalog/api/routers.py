from fastapi import APIRouter, status

from library_api.catalog.api.deps import AuthorServiceDep, BookServiceDep
from library_api.catalog.api.schemas import AuthorCreate, AuthorRead, AuthorUpdate, BookCreate, BookRead, BookUpdate
from library_api.catalog.domain.entities import Book
from library_api.catalog.service_layer.services import AuthorService

router = APIRouter()

authors_router = APIRouter(prefix="/authors", tags=["authors"])
books_router = APIRouter(prefix="/books", tags=["books"])


async def _to_book_read(book: Book, author_service: AuthorService) -> BookRead:
    author = await author_service.get(book.author_id)
    return BookRead(
        id=book.id,
        title=book.title,
        isbn=book.isbn,
        category=book.category,
        author_id=book.author_id,
        author_name=author.name,
        total_copies=book.total_copies,
        available_copies=book.available_copies,
    )


@authors_router.post("", response_model=AuthorRead, status_code=status.HTTP_201_CREATED)
async def create_author(data: AuthorCreate, service: AuthorServiceDep) -> AuthorRead:
    return await service.create(name=data.name, bio=data.bio)


@authors_router.get("", response_model=list[AuthorRead])
async def list_authors(service: AuthorServiceDep, offset: int = 0, limit: int = 100) -> list[AuthorRead]:
    return list(await service.list(offset=offset, limit=limit))


@authors_router.get("/{author_id}", response_model=AuthorRead)
async def get_author(author_id: int, service: AuthorServiceDep) -> AuthorRead:
    return await service.get(author_id)


@authors_router.patch("/{author_id}", response_model=AuthorRead)
async def update_author(author_id: int, data: AuthorUpdate, service: AuthorServiceDep) -> AuthorRead:
    return await service.update(author_id, name=data.name, bio=data.bio)


@authors_router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(author_id: int, service: AuthorServiceDep) -> None:
    await service.delete(author_id)


@books_router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(data: BookCreate, service: BookServiceDep, author_service: AuthorServiceDep) -> BookRead:
    book = await service.create(
        title=data.title,
        isbn=data.isbn,
        category=data.category,
        author_id=data.author_id,
        total_copies=data.total_copies,
    )
    return await _to_book_read(book, author_service)


@books_router.get("", response_model=list[BookRead])
async def list_books(
    service: BookServiceDep, author_service: AuthorServiceDep, offset: int = 0, limit: int = 100
) -> list[BookRead]:
    books = await service.list(offset=offset, limit=limit)
    return [await _to_book_read(book, author_service) for book in books]


@books_router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: int, service: BookServiceDep, author_service: AuthorServiceDep) -> BookRead:
    book = await service.get(book_id)
    return await _to_book_read(book, author_service)


@books_router.patch("/{book_id}", response_model=BookRead)
async def update_book(
    book_id: int, data: BookUpdate, service: BookServiceDep, author_service: AuthorServiceDep
) -> BookRead:
    book = await service.update(
        book_id, title=data.title, category=data.category, total_copies=data.total_copies
    )
    return await _to_book_read(book, author_service)


@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, service: BookServiceDep) -> None:
    await service.delete(book_id)


router.include_router(authors_router)
router.include_router(books_router)
