from httpx import AsyncClient


async def _create_book(client: AsyncClient, *, total_copies: int = 1) -> int:
    author = await client.post("/api/v1/authors", json={"name": "Ada Lovelace"})
    book = await client.post(
        "/api/v1/books",
        json={
            "title": "Livro Teste",
            "isbn": f"isbn-{total_copies}",
            "category": "tech",
            "author_id": author.json()["id"],
            "total_copies": total_copies,
        },
    )
    return book.json()["id"]


async def _create_member(client: AsyncClient) -> int:
    response = await client.post("/api/v1/members", json={"name": "Fulano", "email": "fulano@test.com"})
    return response.json()["id"]


async def test_loan_and_return_flow(client: AsyncClient) -> None:
    book_id = await _create_book(client, total_copies=1)
    member_id = await _create_member(client)

    loan_response = await client.post("/api/v1/loans", json={"book_id": book_id, "member_id": member_id})
    assert loan_response.status_code == 201
    loan_body = loan_response.json()
    assert loan_body["book_title"] == "Livro Teste"
    assert loan_body["member_name"] == "Fulano"
    loan_id = loan_body["id"]

    book_after_loan = await client.get(f"/api/v1/books/{book_id}")
    assert book_after_loan.json()["available_copies"] == 0

    return_response = await client.post(f"/api/v1/loans/{loan_id}/return")
    assert return_response.status_code == 200
    assert return_response.json()["returned_at"] is not None

    book_after_return = await client.get(f"/api/v1/books/{book_id}")
    assert book_after_return.json()["available_copies"] == 1


async def test_loan_book_without_available_copies_returns_409(client: AsyncClient) -> None:
    book_id = await _create_book(client, total_copies=1)
    member_id = await _create_member(client)

    first = await client.post("/api/v1/loans", json={"book_id": book_id, "member_id": member_id})
    assert first.status_code == 201

    second = await client.post("/api/v1/loans", json={"book_id": book_id, "member_id": member_id})
    assert second.status_code == 409
