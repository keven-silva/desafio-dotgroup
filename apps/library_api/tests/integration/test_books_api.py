from httpx import AsyncClient


async def _create_author(client: AsyncClient) -> int:
    response = await client.post("/api/v1/authors", json={"name": "Robert C. Martin"})
    assert response.status_code == 201
    return response.json()["id"]


async def test_create_and_get_book(client: AsyncClient) -> None:
    author_id = await _create_author(client)

    create_response = await client.post(
        "/api/v1/books",
        json={
            "title": "Clean Code",
            "isbn": "978-0132350884",
            "category": "tech",
            "author_id": author_id,
            "total_copies": 3,
        },
    )
    assert create_response.status_code == 201
    body = create_response.json()
    assert body["available_copies"] == 3

    get_response = await client.get(f"/api/v1/books/{body['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Clean Code"


async def test_create_book_with_duplicate_isbn_returns_409(client: AsyncClient) -> None:
    author_id = await _create_author(client)
    payload = {
        "title": "Clean Code",
        "isbn": "978-0132350884",
        "category": "tech",
        "author_id": author_id,
        "total_copies": 1,
    }

    first = await client.post("/api/v1/books", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/books", json=payload)
    assert second.status_code == 409


async def test_get_unknown_book_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/books/999")
    assert response.status_code == 404
