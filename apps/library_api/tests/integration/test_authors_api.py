from httpx import AsyncClient


async def test_create_author_with_duplicate_name_returns_409(client: AsyncClient) -> None:
    first = await client.post("/api/v1/authors", json={"name": "Robert C. Martin"})
    assert first.status_code == 201

    second = await client.post("/api/v1/authors", json={"name": "Robert C. Martin"})
    assert second.status_code == 409


async def test_create_author_with_duplicate_name_different_case_returns_409(client: AsyncClient) -> None:
    first = await client.post("/api/v1/authors", json={"name": "Robert C. Martin"})
    assert first.status_code == 201

    second = await client.post("/api/v1/authors", json={"name": "ROBERT c. MARTIN"})
    assert second.status_code == 409


async def test_update_author_to_an_existing_name_returns_409(client: AsyncClient) -> None:
    await client.post("/api/v1/authors", json={"name": "Robert C. Martin"})
    other = await client.post("/api/v1/authors", json={"name": "Ada Lovelace"})
    other_id = other.json()["id"]

    response = await client.patch(f"/api/v1/authors/{other_id}", json={"name": "robert c. martin"})
    assert response.status_code == 409


async def test_create_author_strips_surrounding_whitespace(client: AsyncClient) -> None:
    response = await client.post("/api/v1/authors", json={"name": "  Robert C. Martin  "})
    assert response.status_code == 201
    assert response.json()["name"] == "Robert C. Martin"


async def test_create_author_with_blank_name_returns_422(client: AsyncClient) -> None:
    response = await client.post("/api/v1/authors", json={"name": "   "})
    assert response.status_code == 422
