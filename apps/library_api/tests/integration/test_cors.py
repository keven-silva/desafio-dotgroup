from httpx import AsyncClient


async def test_health_responds_with_cors_headers_for_cross_origin_request(client: AsyncClient) -> None:
    response = await client.get("/health", headers={"Origin": "https://example.com"})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"
